"""Cross-repo check: run the sibling review-demo-exporter and parse its real output.

Skipped when the exporter checkout is not next to this repo.
"""

import pathlib
import subprocess
import sys
import unittest

from consumer.notes_reader import parse_notes

EXPORTER = pathlib.Path(__file__).resolve().parent.parent.parent / "review-demo-exporter"


@unittest.skipUnless((EXPORTER / "exporter" / "notes_export.py").exists(), "sibling exporter repo not found")
class ExporterIntegrationTests(unittest.TestCase):
    def test_live_exporter_output_matches_contract(self):
        result = subprocess.run(
            [sys.executable, "-m", "exporter.notes_export"],
            cwd=EXPORTER,
            capture_output=True,
            text=True,
            check=True,
        )
        notes = parse_notes(result.stdout)
        self.assertEqual(len(notes), 3)
        self.assertTrue(all("created_at" in n and "title" in n for n in notes))


if __name__ == "__main__":
    unittest.main()
