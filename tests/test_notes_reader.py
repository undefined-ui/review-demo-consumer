import json
import pathlib
import unittest
from datetime import datetime, timezone

from consumer.notes_reader import ContractError, digest, load_notes, parse_notes

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "notes.json"


def _fixture_with(mutate):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for item in data:
        mutate(item)
    return json.dumps(data)


class HappyPathTests(unittest.TestCase):
    def test_reads_fixture(self):
        notes = load_notes(str(FIXTURE))
        self.assertEqual(len(notes), 3)
        self.assertEqual(notes[0]["title"], "Groceries")
        self.assertEqual(notes[0]["created_at"], datetime(2026, 9, 1, 8, 30, tzinfo=timezone.utc))

    def test_digest_is_newest_first(self):
        lines = digest(load_notes(str(FIXTURE)))
        self.assertEqual(
            lines,
            ["2026-09-28  Ideas", "2026-09-15  Review tool demo", "2026-09-01  Groceries"],
        )


class ContractTests(unittest.TestCase):
    def test_missing_created_at_is_rejected(self):
        payload = _fixture_with(lambda n: n.pop("created_at"))
        with self.assertRaisesRegex(ContractError, "created_at"):
            parse_notes(payload)

    def test_renamed_created_at_is_rejected(self):
        # e.g. an upstream change from created_at -> createdAt must not pass silently
        payload = _fixture_with(lambda n: n.__setitem__("createdAt", n.pop("created_at")))
        with self.assertRaisesRegex(ContractError, "created_at"):
            parse_notes(payload)

    def test_missing_title_is_rejected(self):
        payload = _fixture_with(lambda n: n.pop("title"))
        with self.assertRaisesRegex(ContractError, "title"):
            parse_notes(payload)

    def test_top_level_must_be_array(self):
        with self.assertRaises(ContractError):
            parse_notes('{"id": 1}')


if __name__ == "__main__":
    unittest.main()
