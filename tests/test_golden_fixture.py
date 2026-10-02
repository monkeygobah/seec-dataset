"""Optional real-data regression: set SEEC_VALIDATION_FIXTURE to an extracted fixture."""
import csv
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


class GoldenFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.fixture = Path(os.environ.get("SEEC_VALIDATION_FIXTURE",
                                          str(cls.repo.parent / "SEEC_VALIDATION_FIXTURE")))
        if not cls.fixture.is_dir():
            if "SEEC_VALIDATION_FIXTURE" in os.environ:
                raise FileNotFoundError(cls.fixture)
            raise unittest.SkipTest("External real-data fixture not installed")

    def test_source_and_reference_integrity(self):
        lines = (self.fixture / "hashes.sha256").read_text().splitlines()
        self.assertEqual(len(lines), 30)
        for line in lines:
            digest, rel = line.split(maxsplit=1)
            with self.subTest(path=rel):
                self.assertEqual(hashlib.sha256((self.fixture / rel.strip()).read_bytes()).hexdigest(), digest)

    def test_documented_cli_golden_outputs_and_reports(self):
        # Run both formats independently. The fixture itself always stays plain CSV.
        for compressed in (False, True):
            with self.subTest(compressed=compressed), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                toolkit = root / "toolkit"
                for name in ("seec_dataset", "scripts"):
                    shutil.copytree(self.repo / name, toolkit / name,
                                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                shutil.copytree(self.fixture / "manifests", toolkit / "data/manifests")
                manifests = toolkit / "data/manifests"
                self.assertFalse(list(manifests.rglob("*.gz")))
                if compressed:
                    for path in manifests.rglob("*.csv"):
                        with gzip.open(str(path) + ".gz", "wb") as f:
                            f.write(path.read_bytes())
                        path.unlink()  # only the temporary copy
                output = root / "output"
                for overwrite, rerun in ((False, False), (False, True), (True, False)):
                    for subset, size in ((6, 224), (7, 512)):
                        cmd = [sys.executable, "-B", f"scripts/build_subset{subset}.py",
                               "--subset0", str(self.fixture / "sources"), "--out", str(output),
                               "--datasets", "cfd", "fiml", "ffhq"]
                        if overwrite:
                            cmd.append("--overwrite")
                        result = subprocess.run(cmd, cwd=toolkit, text=True, capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        reference = self.fixture / "reference_outputs" / f"SUBSET_{subset}"
                        actual = output / f"SUBSET_{subset}"
                        expected = {p.relative_to(reference).as_posix(): p for p in reference.rglob("*") if p.is_file()}
                        generated = {p.relative_to(actual).as_posix(): p for p in actual.rglob("*") if p.is_file()}
                        self.assertEqual(len(expected), 12)
                        self.assertEqual(set(generated), set(expected))
                        for name, ref in expected.items():
                            with self.subTest(subset=subset, output=name, rerun=rerun, overwrite=overwrite):
                                self.assertEqual(hashlib.sha256(generated[name].read_bytes()).hexdigest(),
                                                 hashlib.sha256(ref.read_bytes()).hexdigest())
                                with Image.open(generated[name]) as image:
                                    self.assertEqual(image.size, (size, size))
                                other = name.replace("_OD_", "_OS_") if "_OD_" in name else name.replace("_OS_", "_OD_")
                                self.assertNotEqual(other, name)
                                self.assertIn(other, generated)
                        with (output / "build_reports" / f"subset{subset}_build_report.csv").open(newline="") as f:
                            reports = list(csv.DictReader(f))
                        self.assertEqual({r["dataset"] for r in reports}, {"cfd", "fiml", "ffhq"})
                        self.assertEqual(len(reports), 3)
                        for row in reports:
                            self.assertEqual(int(row["expected"]), 4)
                            self.assertEqual(int(row["written"]), 0 if rerun else 4)
                            self.assertEqual(int(row["skipped"]), 4 if rerun else 0)
                            for key in ("missing_source", "missing_manifest", "failed"):
                                self.assertEqual(int(row[key]), 0)
                    all_files = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
                    image_files = {p.relative_to(output).as_posix() for s in (6, 7)
                                   for p in (output / f"SUBSET_{s}").rglob("*") if p.is_file()}
                    self.assertEqual(all_files - image_files,
                                     {"build_reports/subset6_build_report.csv", "build_reports/subset7_build_report.csv"})
                    self.assertEqual(len(image_files), 24)


if __name__ == "__main__":
    unittest.main()
