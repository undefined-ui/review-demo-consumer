# review-demo-consumer

Test fixture for evaluating a code-review tool. Not production code.

Reads the JSON produced by [review-demo-exporter](../review-demo-exporter) and prints a digest,
newest note first. It depends on two fields of every note: `title` and `created_at`.
Anything else is ignored; a missing or renamed required field is a `ContractError`.

```bash
python -m consumer.notes_reader fixtures/notes.json
python -m unittest -v
```

`tests/test_exporter_integration.py` runs the sibling exporter checkout (if present at
`../review-demo-exporter`) and validates its live output against this contract.
