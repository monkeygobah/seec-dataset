# Manifest Schema

The manifests in `data/manifests/` are the source of truth for reconstruction.

## Subset 1 Alignment

`subset1_alignment/subset1_{dataset}.csv.gz`

Important columns:

- `rel_src`: source image path relative to `SUBSET_0`
- `rel_dst`: aligned image identity used by later manifests
- `rot_angle_deg_pil`: rotation parameter replayed with Pillow
- `status`: only `OK` rows are used

## Subset 3 Bilateral Crops

`subset3_bilateral_crops/{dataset}_subset3_log.csv.gz`

Important columns:

- `rel_dst_rfc`: bilateral crop identity
- `rel_key_r`: key into the Subset 1 alignment manifest
- `crop_x0_used`, `crop_y0_used`, `crop_x1_used`, `crop_y1_used`: crop box in rotated image coordinates
- `status`: only `CROPPED` rows are used

## Subset 4 Measurements

`data/metadata/periorbital_measurements/{dataset}_periorbital_measurements_final.csv.gz`

Important columns:

- `image_id`: bilateral crop ID without extension
- `orig_file`: bilateral crop filename
- measurement and quality-control columns used as released pseudolabels

## Subset 5 Split

`subset5_unilateral_split/s3_to_s5__{dataset}.csv.gz`

Important columns:

- `rel_src`: bilateral crop identity from Subset 3
- `rel_dst_od`: right-eye output path
- `rel_dst_os`: left-eye output path
- `mid`: vertical split coordinate
- `status`: only `OK` rows are used

## Subset 6/7 Resize

`subset6_7_resize/{dataset}_subset6_224_subset7_512_manifest.csv.gz`

Important columns:

- `src_rel`: Subset 5 source image identity
- `s6_written`, `s6_rel`: 224 by 224 output membership and filename
- `s7_written`, `s7_rel`: 512 by 512 output membership and filename
- `status`: only `ok` rows are used

