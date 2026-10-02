"""Small synthetic reconstruction tests; no released images or manifests needed."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from seec_dataset import builders, io, replay


class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        self.source = self.root / "SUBSET_0"
        self.out = self.root / "output"
        self.names = ["a", "b", "c"]
        self.s1, self.s3, self.s5, self.s67, metadata = [], [], [], [], []
        for name in self.names:
            src = self.source / "celeb" / (name + ".png")
            src.parent.mkdir(parents=True, exist_ok=True)
            with Image.new("RGB", (8, 4)) as image:
                image.paste((200, 10, 20), (0, 0, 4, 4))
                image.paste((10, 20, 200), (4, 0, 8, 4))
                image.save(src)
            self.s1.append(dict(rel_src="celeb/" + src.name,
                                rel_dst=f"celeb/{name}_r.jpg",
                                rot_angle_deg_pil="0", status="OK"))
            self.s3.append(dict(rel_dst_rfc=f"celeb/{name}_rfc.jpg",
                                rel_key_r=f"celeb/{name}_r.jpg",
                                crop_x0_used="0", crop_y0_used="0",
                                crop_x1_used="8", crop_y1_used="4", status="CROPPED"))
            self.s5.append(dict(rel_src=f"celeb/{name}_rfc.jpg",
                                rel_dst_od=f"celeb/{name}_rfc_OD.jpg",
                                rel_dst_os=f"celeb/{name}_rfc_OS.jpg", mid="4", status="OK"))
            for side in ("OD", "OS"):
                self.s67.append(dict(src_rel=f"{name}_rfc_{side}.jpg",
                                     s6_written="True", s6_rel=f"{name}_rfc_{side}_224.jpg",
                                     s7_written="True", s7_rel=f"{name}_rfc_{side}_512.jpg",
                                     status="ok"))
            metadata.append(dict(orig_file=f"{name}_rfc.jpg", image_id=f"{name}_rfc"))
        self.write_csv("manifests/subset1_alignment/subset1_celeb.csv", self.s1)
        self.write_csv("manifests/subset3_bilateral_crops/celeb_subset3_log.csv", self.s3)
        self.write_csv("manifests/subset5_unilateral_split/s3_to_s5__celeb.csv", self.s5)
        self.write_csv("manifests/subset6_7_resize/celeb_subset6_224_subset7_512_manifest.csv", self.s67)
        self.write_csv("metadata/periorbital_measurements/celeb_periorbital_measurements_final.csv", metadata)
        patcher = patch.object(io, "data_root", return_value=self.data)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_csv(self, rel, rows):
        path = self.data / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def build(self, subset, overwrite=False):
        if subset == 4:
            return builders.build_subset4("celeb", self.source, self.out, overwrite)
        if subset == 5:
            return builders.build_subset5("celeb", self.source, self.out, overwrite)
        return builders.build_resized_subset("celeb", self.source, self.out, f"S{subset}", overwrite)

    def assert_balanced(self, stats):
        self.assertEqual(stats.expected, stats.written + stats.skipped +
                         stats.missing_source + stats.missing_manifest + stats.failed)

    def test_reruns_skip_without_replaying_and_overwrite_writes(self):
        for subset in (4, 5, 6, 7):
            with self.subTest(subset=subset):
                count = 3 if subset == 4 else 6
                first = self.build(subset)
                self.assertEqual(first.written, count)
                self.assertEqual(first.skipped, 0)
                with patch.object(builders, "replay_bilateral_crop") as crop:
                    rerun = self.build(subset)
                    crop.assert_not_called()
                self.assertEqual(rerun.written, 0)
                self.assertEqual(rerun.skipped, count)
                overwritten = self.build(subset, overwrite=True)
                self.assertEqual(overwritten.written, count)
                self.assertEqual(overwritten.skipped, 0)
                for stats in (first, rerun, overwritten):
                    self.assert_balanced(stats)

    def test_missing_sources_and_corrupt_images_are_distinct(self):
        (self.source / "celeb/a.png").unlink()
        (self.source / "celeb/b.png").write_bytes(b"not an image")
        for subset in (4, 5, 6, 7):
            with self.subTest(subset=subset):
                stats = self.build(subset)
                count = 1 if subset == 4 else 2
                self.assertEqual((stats.written, stats.missing_source, stats.failed),
                                 (count, count, count))
                self.assert_balanced(stats)

    def test_missing_alignment_and_crop_rows_are_reported(self):
        self.write_csv("manifests/subset1_alignment/subset1_celeb.csv", self.s1[1:])
        self.write_csv("manifests/subset3_bilateral_crops/celeb_subset3_log.csv", [self.s3[0], self.s3[2]])
        for subset in (4, 5, 6, 7):
            with self.subTest(subset=subset):
                stats = self.build(subset)
                count = 1 if subset == 4 else 2
                self.assertEqual(stats.missing_manifest, 2 * count)
                self.assertEqual(stats.written, count)
                self.assert_balanced(stats)

    def test_missing_split_rows_are_reported_for_resize(self):
        self.write_csv("manifests/subset5_unilateral_split/s3_to_s5__celeb.csv", self.s5[1:])
        for subset in (6, 7):
            with self.subTest(subset=subset):
                stats = self.build(subset)
                self.assertEqual((stats.written, stats.missing_manifest), (4, 2))
                self.assert_balanced(stats)

    def test_output_failures_are_not_missing_sources(self):
        for subset in (4, 5, 6, 7):
            with self.subTest(subset=subset):
                save = "save_jpeg" if subset < 6 else "save_square_jpeg"
                with patch.object(builders, save, side_effect=FileNotFoundError("output unavailable")):
                    stats = self.build(subset)
                self.assertEqual(stats.failed, stats.expected)
                self.assertEqual(stats.missing_source, 0)
                self.assert_balanced(stats)

    def test_save_time_skip_is_counted(self):
        for subset in (4, 5, 6, 7):
            with self.subTest(subset=subset):
                save = "save_jpeg" if subset < 6 else "save_square_jpeg"
                with patch.object(builders, save, return_value=False):
                    stats = self.build(subset)
                self.assertEqual(stats.skipped, stats.expected)
                self.assertEqual(stats.written, 0)
                self.assert_balanced(stats)

    def test_cache_bounds_and_closes_images_including_on_failure(self):
        original = builders.replay_bilateral_crop
        for subset in (5, 6, 7):
            for fail in (False, True):
                with self.subTest(subset=subset, fail=fail):
                    live, peak, calls = 0, 0, 0

                    def tracked(*args, **kwargs):
                        nonlocal live, peak, calls
                        image = original(*args, **kwargs)
                        live += 1
                        peak = max(peak, live)
                        calls += 1
                        close = image.close

                        def release():
                            nonlocal live
                            live -= 1
                            close()
                        image.close = release
                        return image

                    save = "save_jpeg" if subset == 5 else "save_square_jpeg"
                    with patch.object(builders, "replay_bilateral_crop", side_effect=tracked):
                        with patch.object(builders, save, side_effect=OSError("write failed") if fail else None,
                                          wraps=None if fail else getattr(builders, save)):
                            stats = self.build(subset, overwrite=True)
                    self.assertEqual(peak, 1)
                    self.assertEqual(live, 0)
                    self.assertEqual(calls, 3)  # adjacent OD/OS reuse the same crop
                    self.assertEqual(stats.failed if fail else stats.written, 6)
                    self.assert_balanced(stats)

    def test_interleaved_resize_targets_keep_outputs_identical(self):
        # Group OD entries first so a single-entry cache must replay evicted crops.
        rows = self.s67[::2] + self.s67[1::2]
        self.write_csv("manifests/subset6_7_resize/celeb_subset6_224_subset7_512_manifest.csv", rows)
        for subset in (5, 6, 7):
            with self.subTest(subset=subset):
                stats = self.build(subset)
                self.assertEqual(stats.written, 6)
                for index, name in enumerate(self.names):
                    with replay.replay_bilateral_crop(self.source, self.s1[index], self.s3[index],
                                                       replay_jpeg_stages=subset in (6, 7)) as crop:
                        for side in ("OD", "OS"):
                            filename = f"{name}_rfc_{side}" + (".jpg" if subset == 5 else f"_{224 if subset == 6 else 512}.jpg")
                            actual = self.out / f"SUBSET_{subset}" / "celeb" / filename
                            reference = self.root / "reference" / filename
                            with replay.split_eye(crop, side, 4) as eye:
                                if subset == 5:
                                    replay.save_jpeg(eye, reference, overwrite=True)
                                else:
                                    with replay.jpeg_roundtrip(eye) as decoded:
                                        replay.save_square_jpeg(decoded, reference, 224 if subset == 6 else 512, overwrite=True)
                            self.assertEqual(actual.read_bytes(), reference.read_bytes())

    def test_jpeg_roundtrip_matches_disk_save_reload(self):
        with Image.open(self.source / "celeb/a.png") as image:
            for options in ({}, {"quality": 95}, {"quality": 95, "subsampling": 0}):
                with self.subTest(options=options):
                    path = self.root / "intermediate.jpg"
                    image.save(path, **options)
                    with Image.open(path) as disk, replay.jpeg_roundtrip(image, **options) as memory:
                        self.assertEqual(disk.convert("RGB").tobytes(), memory.tobytes())

    def test_alignment_override_is_explicit(self):
        self.assertEqual(replay.ALIGNMENT_JPEG_OVERRIDES, {"fiml": {"subsampling": 0}})
        for dataset, expected in (("celeb", {"quality": 95}), ("cfd", {"quality": 95}),
                                  ("ffhq", {"quality": 95}), ("fiml", {"quality": 95, "subsampling": 0})):
            with self.subTest(dataset=dataset):
                row = dict(self.s1[0], rel_src=dataset + "/a.png")
                folder = self.source / dataset
                folder.mkdir(exist_ok=True)
                if not (folder / "a.png").exists():
                    (folder / "a.png").write_bytes((self.source / "celeb/a.png").read_bytes())
                original = replay.jpeg_roundtrip
                with patch.object(replay, "jpeg_roundtrip", wraps=original) as encode:
                    with replay.replay_bilateral_crop(self.source, row, self.s3[0], replay_jpeg_stages=True):
                        pass
                self.assertEqual(encode.call_args_list[0].kwargs, expected)
                self.assertEqual(encode.call_args_list[1].kwargs, {})

    def test_report_contains_skipped_and_balanced_counts(self):
        self.build(6)
        stats = self.build(6)
        builders.write_subset_report(self.out, "SUBSET6", [stats])
        with (self.out / "build_reports/subset6_build_report.csv").open(newline="") as f:
            row = next(csv.DictReader(f))
        self.assertEqual(row["written"], "0")
        self.assertEqual(row["skipped"], "6")
        self.assertEqual(row["expected"], "6")

    def test_output_directory_collision_is_failed_not_skipped(self):
        dst = self.out / "SUBSET_6/celeb/a_rfc_OD_224.jpg"
        dst.mkdir(parents=True)
        stats = self.build(6)
        self.assertEqual((stats.failed, stats.skipped, stats.written), (1, 0, 5))
        self.assert_balanced(stats)


if __name__ == "__main__":
    unittest.main()
