from __future__ import annotations

import csv
import gzip
from pathlib import Path
from typing import Iterable


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def data_root() -> Path:
    return package_root() / "data"


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", newline="", encoding="utf-8")
    return path.open("r", newline="", encoding="utf-8")


def csv_rows(path: Path) -> Iterable[dict[str, str]]:
    with open_text(path) as f:
        yield from csv.DictReader(f)


def first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    joined = ", ".join(str(p) for p in paths)
    raise FileNotFoundError(f"Missing required file. Tried: {joined}")


def manifest_path(group: str, filename: str) -> Path:
    base = data_root() / "manifests" / group
    return first_existing(base / filename, base / f"{filename}.gz")


def metadata_path(dataset: str) -> Path:
    base = data_root() / "metadata" / "periorbital_measurements"
    name = f"{dataset}_periorbital_measurements_final.csv"
    return first_existing(base / name, base / f"{name}.gz")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def normalize_rel(value: str | Path) -> str:
    return str(value).replace("\\", "/").lstrip("./")

