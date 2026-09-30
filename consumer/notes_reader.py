"""Read the JSON produced by review-demo-exporter and print a digest.

Expected input contract (from review-demo-exporter):
    a JSON array of objects, each containing at least
        title       string
        created_at  ISO-8601 timestamp string
"""

from __future__ import annotations

import json
import sys
from datetime import datetime

REQUIRED_FIELDS = ("title", "created_at")


class ContractError(ValueError):
    """Raised when the exporter output does not match the expected contract."""


def validate_note(raw: dict, index: int) -> None:
    if not isinstance(raw, dict):
        raise ContractError(f"note #{index}: expected object, got {type(raw).__name__}")
    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        raise ContractError(f"note #{index}: missing required field(s): {', '.join(missing)}")


def parse_notes(payload: str) -> list[dict]:
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ContractError("expected a JSON array at top level")
    notes = []
    for i, raw in enumerate(data):
        validate_note(raw, i)
        notes.append(
            {
                "title": raw["title"],
                "created_at": datetime.fromisoformat(raw["created_at"]),
            }
        )
    return notes


def load_notes(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return parse_notes(fh.read())


def digest(notes: list[dict]) -> list[str]:
    """One line per note: date then title, newest first."""
    ordered = sorted(notes, key=lambda n: n["created_at"], reverse=True)
    return [f"{n['created_at']:%Y-%m-%d}  {n['title']}" for n in ordered]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        sys.stderr.write("usage: python -m consumer.notes_reader <notes.json>\n")
        return 2
    try:
        notes = load_notes(argv[0])
    except ContractError as exc:
        sys.stderr.write(f"contract error: {exc}\n")
        return 1
    for line in digest(notes):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
