#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seec_dataset.builders import build_subset4, write_subset_report
from seec_dataset.cli import parser, validate_subset0


def main() -> None:
    args = parser("Rebuild SEEC-DATASET Subset 4 from local SUBSET_0 images.").parse_args()
    validate_subset0(args.subset0, args.datasets)
    stats = []
    for dataset in args.datasets:
        print(f"[S4] {dataset}")
        stats.append(build_subset4(dataset, args.subset0, args.out, overwrite=args.overwrite))
    write_subset_report(args.out, "subset4", stats)


if __name__ == "__main__":
    main()

