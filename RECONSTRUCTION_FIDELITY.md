# Reconstruction fidelity

SUBSET_6/7 replay historical intermediate JPEG save/reload stages in memory:

| Stage | JPEG settings |
|---|---|
| Alignment | Quality 95; default Pillow subsampling, except FIML uses `subsampling=0` |
| Bilateral crop | Default Pillow JPEG settings |
| Unilateral crop | Default Pillow JPEG settings |
| Final resize/output | Lanczos to 224/512 square pixels; quality 95, `subsampling=0` |

Those intermediate encodings affect pixels and final hashes. No intermediate files are written; the bilateral crop cache holds at most one image. Existing outputs are skipped without validation: use a fresh directory or `--overwrite` to replace outputs generated before the fidelity fix.

The local historical alignment and bilateral-crop writers confirm the common settings. The FIML-specific alignment and unilateral-split scripts were unavailable locally; these settings follow the supplied historical behavior and exact golden-reference matches.

## Golden regression

The expanded external fixture covers all 14 source datasets: 17 sources, 34 SUBSET_6 outputs, and 30 SUBSET_7 outputs. Celeb and VGG have SUBSET_6 references only. All **64 output SHA256 hashes match** in the validated environment below.

Place the extracted fixture at `../SEEC_VALIDATION_FIXTURE`, or set `SEEC_VALIDATION_FIXTURE` to its directory. Then run:

```bash
python -B -m unittest discover -s tests -v
```

The test discovers fixture datasets, runs the public reconstruction commands in temporary toolkit copies, and checks source/reference hashes, filenames, OD/OS pairs, dimensions, counts, and first-run/rerun/overwrite reports. Plain CSV and compressed copies are tested independently. Without the external fixture, golden tests explicitly skip; no real images are committed.

## Validated environment

Windows; Python 3.13.7; Pillow 12.1.1; libjpeg-turbo 3.1.3 (JPEG API 8.0). Repeated overwrites reproduce the same golden bytes.

Byte-identical JPEG output may depend on the Pillow/libjpeg implementation. The broad `Pillow>=9.0` requirement does not guarantee identical bytes on every build; run the golden regression in your reconstruction environment. The fixture validates selected images from every source, not every corpus image.

External artifact permissions remain a [release-packaging TODO](PROVENANCE_AND_LICENSE.md); these fidelity checks do not grant image or manifest permissions.
