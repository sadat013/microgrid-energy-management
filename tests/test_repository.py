"""Non-invasive structural checks; these tests do not run simulations."""

import ast
import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "src" / "python"
DATA_DIR = ROOT / "data" / "raw"


class RepositoryChecks(unittest.TestCase):
    def test_python_sources_parse(self):
        for path in sorted(SOURCE_DIR.glob("*.py")):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_required_data_files(self):
        expected = {"EV.csv", "Load.csv", "P_loss.csv", "PV.csv", "T_set.csv"}
        self.assertEqual(expected, {path.name for path in DATA_DIR.glob("*.csv")})

    def test_scenario_data_shape(self):
        for path in sorted(DATA_DIR.glob("*.csv")):
            with self.subTest(path=path.name):
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    rows = list(csv.reader(stream, delimiter=";"))
                self.assertEqual(962, len(rows))  # header plus 961 samples
                self.assertEqual(["S1", "S2", "S3", "S4"], rows[0][1:])
                self.assertTrue(all(len(row) == 5 for row in rows))
                self.assertTrue(all(cell != "" for row in rows[1:] for cell in row))


if __name__ == "__main__":
    unittest.main()
