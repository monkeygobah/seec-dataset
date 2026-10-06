# SEEC Dataset Reconstruction Toolkit

SEEC (Standardized External-Eye Corpus) was designed for external-eye/periocular representation learning and benchmarking. This toolkit reconstructs its **224 x 224 unilateral images (SUBSET_6)** and eligible **512 x 512 images (SUBSET_7)** from permitted local source images and released manifests.

Original images, reconstructed crops, and restricted clinical cohorts are not bundled. The tools replay recorded transformations and do not rerun landmark detection or CNN filtering.

## 1. Install

Clone this repository and run commands from its root. Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
```

## 2. Download the reconstruction manifests

Download the [current manifest archives](https://drive.google.com/file/d/1nkO4BrKuK3BiTK6PA_bHB7ph8fECHU0g/view?usp=drive_link). 

Extract the archive's `manifests/`, `metadata/`, and `tables/` folders **into this repository's `data/` directory**:

```text
data/
  manifests/
    subset1_alignment/
    subset2_filtering/
    subset3_bilateral_crops/
    subset4_membership/
    subset5_unilateral_split/
    subset6_7_resize/
  metadata/periorbital_measurements/
  tables/
```

Avoid an extra archive folder or `data/data/` nesting. SUBSET_6/7 use only the alignment, bilateral-crop, unilateral-split, and resize manifests. Measurement metadata is unnecessary for these builds. See [Manifest Schema](MANIFEST_SCHEMA.md).

## 3. Arrange source images in SUBSET_0

1. Obtain the source datasets you are permitted to use from the providers listed in [Provenance and Licensing](SOURCE_DATASETS.md). You can reconstruct only the datasets you have; select them with `--datasets` in step 4.
2. Create a source-image folder called `SUBSET_0` anywhere on your computer. Inside it, use the dataset keys from the manifests, such as `celeb`, `cfd`, or `ffhq`.
3. Place each source image at `SUBSET_0/<rel_src>`, where `rel_src` is recorded in `data/manifests/subset1_alignment/subset1_{dataset}.csv` or `.csv.gz`. Keep any subdirectories in that path.

For example, these real manifest entries require:

```text
SUBSET_0/
  celeb/000001.jpg
  cfd/CFD-AF-200-228-N.jpg
  ffhq/00000.png
```

Pass the parent `SUBSET_0` folder to `--subset0`, rather than an individual dataset folder. For example, a CelebA-only build uses `--subset0 /path/to/SUBSET_0 --datasets celeb`.

To inspect the first five usable source paths for a dataset, run this from the toolkit root after extracting the manifests. Replace `celeb` with your dataset key:

```bash
python -c "from itertools import islice; from seec_dataset.io import csv_rows; from seec_dataset.replay import s1_log; rows = (r for r in csv_rows(s1_log('celeb')) if r['status'] == 'OK'); print('\n'.join(r['rel_src'] for r in islice(rows, 5)))"
```

Use the matching source-image edition and dimensions: `rot_old_w` and `rot_old_h` record the expected input width and height. Example entries are:

| Dataset key | Expected source path | Input pixels |
|---|---|---|
| `celeb` | `celeb/000001.jpg` | 178 x 218 |
| `cfd` | `cfd/CFD-AF-200-228-N.jpg` | 2444 x 1718 |
| `ffhq` | `ffhq/00000.png` | 1024 x 1024 |
| `fiml` | `fiml/fiml_00000000.jpg` | 512 x 512 |
| `umd` | `umd/umd_00000000.jpg` | 256 x 256 |
| `vgg` | `vgg/0.jpg` | 112 x 112 |

These are examples, not a complete file list. Preserve the matching input pixels when arranging files; resizing or cropping them changes the coordinates used for reconstruction.

If your download uses different filenames or an array/archive format, it must first be matched to the manifest's image identities and exported in the corresponding image form. This toolkit provides no downloaders, conversion recipes, or original-to-prepared filename maps. A file renamed to an expected name is usable only if it is the corresponding source image; matching the name alone is insufficient.

## 4. Reconstruct 224 or 512 images

For a partial build, select only the datasets you have:

```bash
python scripts/build_subset6.py --subset0 /path/to/SUBSET_0 --out /path/to/output --datasets celeb
python scripts/build_subset7.py --subset0 /path/to/SUBSET_0 --out /path/to/output --datasets celeb
```

Each command reads directly from `SUBSET_0`; earlier subset builds are unnecessary. Omit `--datasets` to request all 14 datasets, or use multiple keys such as `--datasets celeb ffhq`. All selected dataset folders must exist.

Outputs:

```text
output/SUBSET_6/{dataset}/*_224.jpg
output/SUBSET_7/{dataset}/*_512.jpg
output/build_reports/subset6_build_report.csv
output/build_reports/subset7_build_report.csv
```

SUBSET_7 contains only manifest-eligible images. Existing image files are skipped; add `--overwrite` to replace them.

## 5. Check the build and prepare benchmark input

Inspect the CSV build report for each selected dataset:

| Field | Meaning |
|---|---|
| `expected` | Requested output images |
| `written` | Images successfully written this run |
| `skipped` | Existing output files left in place |
| `missing_source` | Required original images unavailable |
| `missing_manifest` | Required joining records unavailable |
| `failed` | Other reconstruction or write errors |

A completed build has zero missing/failed counts and `written + skipped = expected`. Skipped files are not revalidated. See [Reconstruction Fidelity](RECONSTRUCTION_FIDELITY.md) for historical JPEG replay and golden regression checks. Missing archive files can stop a command before a report is produced; a command finishing does not guarantee a complete build.

Use the canonical [SEEC benchmark Quickstart](https://github.com/monkeygobah/seec-benchmark/blob/main/QUICKSTART.md) and its `scripts/prepare_benchmark_layout.py` to prepare reconstructed SUBSET_6/7 for the fixed benchmark manifests. Partial reconstruction may not satisfy every benchmark entry; do not regenerate fixed splits.

## Optional and legacy outputs

`scripts/build_subset5.py` reconstructs unresized unilateral OD/OS images into `output/SUBSET_5/{dataset}/` with the same input flags.

**Legacy/experimental, outside the submitted benchmark:** `scripts/build_subset4.py` reconstructs bilateral crops and copies released periorbital-distance measurement pseudolabels. It additionally requires `data/metadata/periorbital_measurements/`. Outputs are `output/SUBSET_4/{dataset}/images/` and `periorbital_metadata/periorbital_measurements_final.csv`. It does not predict measurements. This workflow is not needed for SUBSET_6/7 or the submitted benchmark.

## Use and permissions

Follow source-specific permissions and citations before reconstruction or redistribution. Periocular cropping reduces but does not eliminate identifiability. SEEC is intended for representation-learning research, not face recognition, identity verification, or clinical deployment. See [licensing and provenance](PROVENANCE_AND_LICENSE.md).
