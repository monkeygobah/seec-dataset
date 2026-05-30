from __future__ import annotations

from pathlib import Path

from .config import S6_SIZE, S7_SIZE
from .io import csv_rows, normalize_rel
from .replay import (
    BuildStats,
    _add,
    copy_metadata,
    load_s1_records,
    load_s3_records,
    load_split_rows,
    metadata_rows,
    replay_bilateral_crop,
    s67_log,
    save_jpeg,
    save_square_jpeg,
    split_eye,
    target_s4_relpaths,
    target_s5_relpaths,
    write_report,
)


def _prepare_crop_maps(dataset: str, target_rel_rfc: set[str]):
    s3 = load_s3_records(dataset, target_rel_rfc)
    s1_keys = {normalize_rel(row["rel_key_r"]) for row in s3.values()}
    s1 = load_s1_records(dataset, s1_keys)
    return s3, s1


def build_subset4(dataset: str, subset0: Path, out: Path, overwrite: bool = False) -> BuildStats:
    target_rel = target_s4_relpaths(dataset)
    s3, s1 = _prepare_crop_maps(dataset, target_rel)
    stats = BuildStats(dataset=dataset, expected=len(target_rel))

    copy_metadata(
        dataset,
        out / "SUBSET_4" / dataset / "periorbital_metadata" / "periorbital_measurements_final.csv",
    )

    for row in metadata_rows(dataset):
        rel_rfc = f"{dataset}/{row['orig_file']}"
        s3_row = s3.get(rel_rfc)
        if s3_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        s1_row = s1.get(normalize_rel(s3_row["rel_key_r"]))
        if s1_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        try:
            crop = replay_bilateral_crop(subset0, s1_row, s3_row)
            dst = out / "SUBSET_4" / dataset / "images" / row["orig_file"]
            save_jpeg(crop, dst, overwrite=overwrite)
            stats = _add(stats, written=1)
        except FileNotFoundError:
            stats = _add(stats, missing_source=1)
        except Exception:
            stats = _add(stats, failed=1)
    return stats


def build_subset5(dataset: str, subset0: Path, out: Path, overwrite: bool = False) -> BuildStats:
    target_rel = target_s5_relpaths(dataset)
    s3, s1 = _prepare_crop_maps(dataset, target_rel)
    split_rows = load_split_rows(dataset)
    stats = BuildStats(dataset=dataset, expected=2 * len(target_rel))
    crop_cache = {}

    for unilateral_rel, split_row in split_rows.items():
        s3_row = s3.get(normalize_rel(split_row["rel_src"]))
        if s3_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        s1_row = s1.get(normalize_rel(s3_row["rel_key_r"]))
        if s1_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        side = "OD" if unilateral_rel.endswith("_OD.jpg") else "OS"
        try:
            crop_key = normalize_rel(split_row["rel_src"])
            if crop_key not in crop_cache:
                crop_cache[crop_key] = replay_bilateral_crop(subset0, s1_row, s3_row)
            crop = crop_cache[crop_key]
            eye = split_eye(crop, side, int(split_row.get("mid") or -1))
            save_jpeg(eye, out / "SUBSET_5" / unilateral_rel, overwrite=overwrite)
            stats = _add(stats, written=1)
        except FileNotFoundError:
            stats = _add(stats, missing_source=1)
        except Exception:
            stats = _add(stats, failed=1)
    return stats


def _resize_targets(dataset: str, subset: str) -> list[dict[str, str]]:
    rows = []
    for row in csv_rows(s67_log(dataset)):
        if row.get("status") != "ok":
            continue
        if subset == "S6" and row.get("s6_written") == "True":
            rows.append(row)
        if subset == "S7" and row.get("s7_written") == "True":
            rows.append(row)
    return rows


def build_resized_subset(
    dataset: str,
    subset0: Path,
    out: Path,
    subset: str,
    overwrite: bool = False,
) -> BuildStats:
    targets = _resize_targets(dataset, subset)
    target_unilateral = {f"{dataset}/{normalize_rel(row['src_rel'])}" for row in targets}
    split_rows = load_split_rows(dataset, target_unilateral)
    target_bilateral = {normalize_rel(row["rel_src"]) for row in split_rows.values()}
    s3, s1 = _prepare_crop_maps(dataset, target_bilateral)
    stats = BuildStats(dataset=dataset, expected=len(targets))
    crop_cache = {}

    size = S6_SIZE if subset == "S6" else S7_SIZE
    out_subset = "SUBSET_6" if subset == "S6" else "SUBSET_7"
    rel_col = "s6_rel" if subset == "S6" else "s7_rel"

    for row in targets:
        unilateral_rel = f"{dataset}/{normalize_rel(row['src_rel'])}"
        split_row = split_rows.get(unilateral_rel)
        if split_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        s3_row = s3.get(normalize_rel(split_row["rel_src"]))
        if s3_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        s1_row = s1.get(normalize_rel(s3_row["rel_key_r"]))
        if s1_row is None:
            stats = _add(stats, missing_manifest=1)
            continue
        side = "OD" if unilateral_rel.endswith("_OD.jpg") else "OS"
        try:
            crop_key = normalize_rel(split_row["rel_src"])
            if crop_key not in crop_cache:
                crop_cache[crop_key] = replay_bilateral_crop(subset0, s1_row, s3_row)
            crop = crop_cache[crop_key]
            eye = split_eye(crop, side, int(split_row.get("mid") or -1))
            dst = out / out_subset / dataset / normalize_rel(row[rel_col])
            save_square_jpeg(eye, dst, size, overwrite=overwrite)
            stats = _add(stats, written=1)
        except FileNotFoundError:
            stats = _add(stats, missing_source=1)
        except Exception:
            stats = _add(stats, failed=1)
    return stats


def write_subset_report(out: Path, subset_name: str, stats: list[BuildStats]) -> None:
    write_report(out / "build_reports" / f"{subset_name.lower()}_build_report.csv", stats)
