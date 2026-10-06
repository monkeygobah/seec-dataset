# Source datasets and release terms

## Software and artifact scope

The toolkit code and documentation are released under the [MIT License](LICENSE). This grant does not cover source images, reconstructed crops, or externally hosted artifacts.

Source-image terms continue to apply to originals and reconstructed crops. The reconstruction manifest archive does not grant permission to download, use, or redistribute source images. The MIT license does not apply to externally hosted manifests or legacy metadata.

This toolkit bundles no source images, derived crops, or restricted clinical cohorts. Clinical benchmark results cannot be publicly reproduced using this release alone.

## Source references

These are the source references already recorded by the toolkit. They are not a guarantee that a download is currently available or matches the manifest's source version.
| Manifest key | Dataset                                 | Reference                                                                                                  |
| ------------ | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `celeb`    | CelebA                                  | [Project](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)                                                |
| `utk`      | UTKFace                                 | [Project](https://susanqq.github.io/UTKFace/)                                                               |
| `ffhq`     | FFHQ                                    | [Repository](https://github.com/nvlabs/ffhq-dataset)                                                        |
| `vgg`      | VGGFace2                                | [Existing distribution reference](https://www.kaggle.com/datasets/yakhyokhuja/vggface2-112x112)             |
| `tufts`    | Tufts Face Database                     | [Provider](https://tdface.ece.tufts.edu/)                                                                   |
| `cfd`      | Chicago Face Database                   | [Provider](https://www.chicagofaces.org/)                                                                   |
| `cfd-mr`   | CFD-MR                                  | [Provider](https://www.chicagofaces.org/)                                                                   |
| `cfd-i`    | CFD-India                               | [Provider](https://www.chicagofaces.org/)                                                                   |
| `imdb`     | IMDB                                    | [IMDB-WIKI project](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/)                                   |
| `wiki`     | WIKI                                    | [IMDB-WIKI project](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/)                                   |
| `umd`      | UMDFaces (Still Images)                 | [Existing distribution reference](https://www.kaggle.com/datasets/meln1337/faces-umd)                       |
| `fiml`     | Face Images with Marked Landmark Points | [Distribution reference](https://www.kaggle.com/datasets/drgilermo/face-images-with-marked-landmark-points) |
| `fei`      | FEI Face Database                       | [Provider](https://fei.edu.br/~cet/facedatabase.html)                                                       |
| `morph`    | MORPH (Academic)                        | [Existing access reference](https://omen.cs.uni-magdeburg.de/disclaimer/index.php)                          |

Follow each provider's license, access, and citation requirements. Use alignment-manifest `rel_src` paths to arrange local files; no additional per-source preparation recipes are supplied here.

## Release Files

The reconstruction archive contains SEEC processing records used to rebuild the corpus, including alignment, cropping, splitting, resizing, and dataset membership information. It does not include source images. The archive also contains legacy SUBSET_4 measurement files from earlier development. These are not part of the submitted benchmark and are not required for benchmark reproduction.

The checkpoint archive contains 36 SEEC-trained models. Eighteen were trained from random initialization and eighteen used ImageNet-pretrained initialization. DINOv2 and MAE checkpoints are not redistributed by SEEC. Source-dataset terms continue to apply to the original images and reconstructed crops. The repository MIT license applies to the software, not to source images or externally hosted release files.

## Intended use and identifiability

SEEC is intended external-eye/periocular representation-learning research and benchmarking. It is not intended for face recognition or identity verification.

Clinical results are research benchmark results, not deployment-ready clinical validation. Legacy SUBSET_4 measurement pseudolabels are experimental and outside the submitted benchmark.
