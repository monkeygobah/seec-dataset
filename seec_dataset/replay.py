from __future__ import annotations

import csv
from io import BytesIO
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from .io import csv_rows, ensure_parent, manifest_path, metadata_path, normalize_rel, open_text

RESAMPLE_LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BILINEAR)

@dataclass(frozen=True)
class BuildStats:
    dataset: str
    expected: int = 0
    written: int = 0
    skipped: int = 0
    missing_source: int = 0
    missing_manifest: int = 0
    failed: int = 0


def _add(stats: BuildStats, **updates: int) -> BuildStats:
    values = stats.__dict__.copy()
    for key, delta in updates.items():
        values[key] += delta
    return BuildStats(**values)


def s1_log(dataset: str) -> Path:
    return manifest_path("subset1_alignment", f"subset1_{dataset}.csv")


def s3_log(dataset: str) -> Path:
    return manifest_path("subset3_bilateral_crops", f"{dataset}_subset3_log.csv")


def s5_log(dataset: str) -> Path:
    return manifest_path("subset5_unilateral_split", f"s3_to_s5__{dataset}.csv")


def s67_log(dataset: str) -> Path:
    return manifest_path("subset6_7_resize", f"{dataset}_subset6_224_subset7_512_manifest.csv")


def load_s3_records(dataset: str, target_rel_rfc: set[str]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for row in csv_rows(s3_log(dataset)):
        rel = normalize_rel(row.get("rel_dst_rfc", ""))
        if rel in target_rel_rfc and row.get("status") == "CROPPED":
            found[rel] = row
    return found


def load_s1_records(dataset: str, target_rel_r: set[str]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for row in csv_rows(s1_log(dataset)):
        rel = normalize_rel(row.get("rel_dst", ""))
        if rel in target_rel_r and row.get("status") == "OK":
            found[rel] = row
    return found


def load_split_rows(dataset: str, target_unilateral_rel: set[str] | None = None) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for row in csv_rows(s5_log(dataset)):
        if row.get("status") != "OK":
            continue
        for col in ("rel_dst_od", "rel_dst_os"):
            rel = normalize_rel(row.get(col, ""))
            if target_unilateral_rel is None or rel in target_unilateral_rel:
                found[rel] = row
    return found


def source_image(subset0: Path, s1_row: dict[str, str]) -> Path:
    return subset0 / normalize_rel(s1_row["rel_src"])


class MissingSourceError(FileNotFoundError):
    """An original image required for reconstruction is missing."""


# The common s0_to_s1.py writer uses quality=95 and Pillow default subsampling.
# FIML's historical 4:4:4 override is confirmed by the real-data golden fixture.
ALIGNMENT_JPEG_OVERRIDES = {"fiml": {"subsampling": 0}}


def jpeg_roundtrip(image: Image.Image, **options) -> Image.Image:
    """Replay an intermediate JPEG file without writing it to disk."""
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG", **options)
        buffer.seek(0)
        with Image.open(buffer) as decoded:
            return decoded.convert("RGB")


def replay_bilateral_crop(
    subset0: Path,
    s1_row: dict[str, str],
    s3_row: dict[str, str],
    *,
    replay_jpeg_stages: bool = False,
) -> Image.Image:
    src = source_image(subset0, s1_row)
    if not src.exists():
        raise MissingSourceError(str(src))

    try:
        opened = Image.open(src)
    except FileNotFoundError as exc:
        raise MissingSourceError(str(src)) from exc
    box = tuple(int(float(s3_row[key])) for key in (
        "crop_x0_used", "crop_y0_used", "crop_x1_used", "crop_y1_used",
    ))
    with opened as original, original.convert("RGB") as img:
        angle = -float(s1_row["rot_angle_deg_pil"])
        with img.rotate(angle, resample=Image.BICUBIC, expand=True) as rotated:
            if not replay_jpeg_stages:
                return rotated.crop(box)
            dataset = normalize_rel(s1_row["rel_src"]).split("/")[0]
            options = {"quality": 95, **ALIGNMENT_JPEG_OVERRIDES.get(dataset, {})}
            with jpeg_roundtrip(rotated, **options) as aligned:
                with aligned.crop(box) as crop:
                    # The historical crop writer calls image.save(path) without options.
                    return jpeg_roundtrip(crop)


def split_eye(crop: Image.Image, side: str, mid: int | None = None) -> Image.Image:
    w, h = crop.size
    split = mid if mid is not None and mid >= 0 else w // 2
    if side == "OD":
        return crop.crop((0, 0, split, h))
    if side == "OS":
        return crop.crop((split, 0, w, h))
    raise ValueError(f"Unknown eye side: {side}")


def save_jpeg(image: Image.Image, dst: Path, overwrite: bool = False) -> bool:
    if dst.is_file() and not overwrite:
        return False
    ensure_parent(dst)
    image.convert("RGB").save(dst)
    return True


def save_square_jpeg(image: Image.Image, dst: Path, size: int, overwrite: bool = False) -> bool:
    if dst.is_file() and not overwrite:
        return False
    ensure_parent(dst)
    resized = image.convert("RGB").resize((size, size), resample=RESAMPLE_LANCZOS)
    resized.save(dst, format="JPEG", quality=95, subsampling=0)
    return True


def write_report(path: Path, rows: Iterable[BuildStats]) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["dataset", "expected", "written", "skipped", "missing_source", "missing_manifest", "failed"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def copy_metadata(dataset: str, out_csv: Path) -> None:
    ensure_parent(out_csv)
    src = metadata_path(dataset)
    with open_text(src) as fin, out_csv.open("w", newline="", encoding="utf-8") as fout:
        shutil.copyfileobj(fin, fout)


def metadata_rows(dataset: str) -> Iterable[dict[str, str]]:
    return csv_rows(metadata_path(dataset))


def target_s4_relpaths(dataset: str) -> set[str]:
    return {f"{dataset}/{row['orig_file']}" for row in metadata_rows(dataset)}


def target_s5_relpaths(dataset: str) -> set[str]:
    return {normalize_rel(row["rel_src"]) for row in csv_rows(s5_log(dataset)) if row.get("status") == "OK"}
