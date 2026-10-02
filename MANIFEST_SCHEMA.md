# Reconstruction Manifest Schema

Extract the [current archive](https://drive.google.com/file/d/1nkO4BrKuK3BiTK6PA_bHB7ph8fECHU0g/view?usp=drive_link) into the repository's `data/` directory as shown in the [README](README.md). Paths below are relative to `data/manifests/`, except the legacy metadata path. The loader accepts `.csv` or `.csv.gz` and prefers `.csv` if both exist.

## Alignment

`subset1_alignment/subset1_{dataset}.csv.gz`

| Column | Used for |
|---|---|
| `rel_src` | Original image path relative to `SUBSET_0` |
| `rel_dst` | Dataset-prefixed aligned-image identity joined by `rel_key_r` |
| `rot_angle_deg_pil` | Pillow rotation; reconstruction uses its negative, bicubic resampling, and `expand=True` |
| `status` | Only `OK` rows are used |

## Bilateral crop

`subset3_bilateral_crops/{dataset}_subset3_log.csv.gz`

| Column | Used for |
|---|---|
| `rel_key_r` | Alignment manifest's `rel_dst` |
| `rel_dst_rfc` | Dataset-prefixed bilateral identity joined by the split manifest |
| `crop_x0_used`, `crop_y0_used`, `crop_x1_used`, `crop_y1_used` | Recorded crop box in rotated-image coordinates |
| `status` | Only `CROPPED` rows are used |

## Unilateral split

`subset5_unilateral_split/s3_to_s5__{dataset}.csv.gz`

| Column | Used for |
|---|---|
| `rel_src` | Bilateral identity matching `rel_dst_rfc` |
| `rel_dst_od`, `rel_dst_os` | Dataset-prefixed unilateral output paths |
| `mid` | Horizontal split coordinate: OD takes the left portion, OS the right; an empty/negative value falls back to half the crop width |
| `status` | Only `OK` rows are used |

## 224/512 resize and membership

`subset6_7_resize/{dataset}_subset6_224_subset7_512_manifest.csv.gz`

| Column | Used for |
|---|---|
| `src_rel` | Unilateral path within the dataset; prepend `{dataset}/` to join the split manifest |
| `s6_written`, `s7_written` | Membership flags; the loader selects the literal value `True` for the requested subset |
| `s6_rel`, `s7_rel` | Output paths within `{dataset}/`, under `SUBSET_6/` or `SUBSET_7/` |
| `status` | Only `ok` rows are used |

SUBSET_6/7 replay alignment, cropping, and splitting directly from originals, then resize with Lanczos to 224/512 square pixels. The `subset2_filtering/`, `subset4_membership/`, and `data/tables/` artifacts are not read by these builders; retained membership comes from the resize manifest.

## Legacy/experimental measurement metadata

`data/metadata/periorbital_measurements/{dataset}_periorbital_measurements_final.csv.gz`

`orig_file` identifies the bilateral filename; `image_id` is its ID without an extension. Other columns contain released measurement/quality metadata. `build_subset4.py` uses `orig_file` to select bilateral images and copies the metadata CSV.

These periorbital-distance pseudolabels are outside the submitted benchmark and are not required by SUBSET_6/7. They are model-generated experimental labels, not clinical ground truth.
