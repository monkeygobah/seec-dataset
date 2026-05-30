# SEEC-DATASET Reconstruction Toolkit

This repository reconstructs the SEEC/UIC-EYE periocular image subsets from locally held source face datasets.

The repository does **not** include original face images or derived cropped image files. Users must obtain the source datasets independently, confirm that they have permission to use them, and arrange them in the expected folder structure before running the scripts.

The reconstruction scripts replay released manifests and metadata. They do **not** rerun CNN filtering, MediaPipe landmark detection, or periorbital distance prediction.

## 1. Install Requirements

```bash
pip install -r requirements.txt
```

Python 3.10+ is recommended.

## 2. Obtain Source Datasets and Permissions

Download the source datasets from their original providers and follow each provider's license, access, and citation requirements.

| Dataset | Source |
|---|---|
| CelebA | https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html |
| UTKFace | https://susanqq.github.io/UTKFace/ |
| FFHQ (Flickr Faces HQ) | https://github.com/nvlabs/ffhq-dataset |
| VGGFace2 | https://www.kaggle.com/datasets/yakhyokhuja/vggface2-112x112 |
| Tufts Face Database | https://tdface.ece.tufts.edu/ |
| Chicago Face Database (CFD) | https://www.chicagofaces.org/ |
| CFD-MR | https://www.chicagofaces.org/ |
| CFD-India | https://www.chicagofaces.org/ |
| IMDB | https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/ |
| WIKI | https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/ |
| UMDFaces (Still Images) | https://www.kaggle.com/datasets/meln1337/faces-umd |
| Face Images with Marked Landmark Points | https://www.kaggle.com/datasets/drgilermo/face-images-with-marked-landmark-points |
| FEI Face Database | https://fei.edu.br/~cet/facedatabase.html |
| MORPH (Academic) | https://uncw.edu/research/innovation/commercialization/technology-portfolio/morph |

## 3. Arrange Source Images

Create a local `SUBSET_0` folder with one folder per dataset:

```text
SUBSET_0/
  celeb/
  cfd/
  cfd-i/
  cfd-mr/
  fei/
  ffhq/
  fiml/
  imdb/
  morph/
  tufts/
  umd/
  utk/
  vgg/
  wiki/
```

Each dataset folder should contain the image files using the same filenames used in the original datasets after any local extraction or conversion you perform. This toolkit does not include dataset downloaders or preprocessing scripts.

If files are missing or named differently, the build scripts will report them in `build_reports/`.

## 4. Download Heavy Reconstruction Files

This toolkit requires released manifests and periorbital measurement metadata.

Download the heavy files here:

```text
https://drive.google.com/drive/folders/1U3T6b5vY-ddJLjdrEDZ169OHI-VFQPc5?usp=drive_link
```

Place or extract them so the repository contains:

```text
data/
  manifests/
  metadata/periorbital_measurements/
  tables/
```

If those folders are already present in your clone, you can skip this step.

## 5. Rebuild Subsets

Run one command for the subset you want to reconstruct. Each command reads directly from `SUBSET_0`; you do not need to run earlier subset commands first.

### Subset 4: Bilateral Periocular Images + Measurements

```bash
python scripts/build_subset4.py --subset0 /path/to/SUBSET_0 --out /path/to/output
```

Writes:

```text
output/SUBSET_4/{dataset}/images/
output/SUBSET_4/{dataset}/periorbital_metadata/periorbital_measurements_final.csv
output/build_reports/subset4_build_report.csv
```

### Subset 5: Unilateral OD/OS Periocular Images

```bash
python scripts/build_subset5.py --subset0 /path/to/SUBSET_0 --out /path/to/output
```

Writes:

```text
output/SUBSET_5/{dataset}/
output/build_reports/subset5_build_report.csv
```

### Subset 6: 224 x 224 Unilateral Images

```bash
python scripts/build_subset6.py --subset0 /path/to/SUBSET_0 --out /path/to/output
```

Writes:

```text
output/SUBSET_6/{dataset}/
output/build_reports/subset6_build_report.csv
```

### Subset 7: 512 x 512 Eligible Unilateral Images

```bash
python scripts/build_subset7.py --subset0 /path/to/SUBSET_0 --out /path/to/output
```

Writes:

```text
output/SUBSET_7/{dataset}/
output/build_reports/subset7_build_report.csv
```

Optional flags:

```bash
--datasets celeb ffhq
--overwrite
```

## Notes

- Subset 4 measurements are provided as released CSV metadata and should be treated as model-generated pseudolabels.
- The scripts generate light build reports with expected, written, missing-source, missing-manifest, and failed counts.
- Large full-dataset builds can take time- we have not yet added logging! 
