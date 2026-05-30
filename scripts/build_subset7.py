#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seec_dataset.builders import build_resized_subset, write_subset_report
from seec_dataset.cli import parser, validate_subset0


def main() -> None:
    args = parser("Rebuild SEEC-DATASET Subset 7 from local SUBSET_0 images.").parse_args()
    validate_subset0(args.subset0, args.datasets)
    stats = []
    for dataset in args.datasets:
        print(f"[S7] {dataset}")
        stats.append(build_resized_subset(dataset, args.subset0, args.out, "S7", overwrite=args.overwrite))
    write_subset_report(args.out, "subset7", stats)


if __name__ == "__main__":
    main()

