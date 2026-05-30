from __future__ import annotations

import argparse
from pathlib import Path

from .config import DATASETS


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--subset0", required=True, type=Path, help="Path to local SUBSET_0 root.")
    p.add_argument("--out", required=True, type=Path, help="Output root where reconstructed subsets are written.")
    p.add_argument(
        "--datasets",
        nargs="+",
        default=DATASETS,
        choices=DATASETS,
        help="Datasets to rebuild. Defaults to all datasets.",
    )
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing reconstructed images.")
    return p


def validate_subset0(subset0: Path, datasets: list[str]) -> None:
    if not subset0.exists():
        raise FileNotFoundError(f"SUBSET_0 root does not exist: {subset0}")
    missing = [ds for ds in datasets if not (subset0 / ds).exists()]
    if missing:
        raise FileNotFoundError(f"Missing dataset folders under SUBSET_0: {', '.join(missing)}")

