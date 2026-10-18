# TinyWMS lesson: 01-json-backbone

## Stage purpose
This stage defines TinyWMS's first concrete data contract: a small inventory JSON file and a simple Python CLI that can read it. Students can inspect the inventory shape directly, then use the CLI to list items, find a SKU, and print valid JSON.

## Files in this lesson
- `data/inventory.json` - realistic sample inventory data with SKU, description, bin location, quantity, and unit fields.
- `data/inventory.schema.json` - JSON Schema for the inventory file so students can compare data to an explicit contract.
- `docs/data-contracts.md` - field-by-field notes for the inventory JSON representation.
- `docs/architecture.md` - the first Component Assembly Map entries for the JSON file and CLI.
- `src/inventory_cli.py` - a small Python CLI that loads inventory JSON, checks required fields, lists items, finds a SKU, and emits JSON.
- `tests/test_inventory_cli.py` - unit tests for the visible inventory CLI behaviors introduced in this lesson.

## Run the lesson
From this folder:
```bash
python3 src/inventory_cli.py data/inventory.json list
python3 src/inventory_cli.py data/inventory.json find SKU-1001
python3 src/inventory_cli.py data/inventory.json dump
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Student exercises
1. Edit `data/inventory.json` to add one more product, then run `python3 src/inventory_cli.py data/inventory.json list` and observe the new line in the output.
2. Change one SKU in `data/inventory.json`, then run `python3 src/inventory_cli.py data/inventory.json find <that-sku>` and confirm the JSON output changes or the CLI reports the SKU is missing.
## Continuity note
- Inherited contract: the repository scaffold and teaching-document structure from Stage 0 remain valid.
- Boundary changed in this stage: TinyWMS now has a visible JSON file boundary and a Python CLI process boundary.

## Component assembly update
- Added: `data/inventory.json`, `data/inventory.schema.json`, `src/inventory_cli.py`, `tests/test_inventory_cli.py`.
- Reused unchanged: the directory scaffold from Stage 0 (`docs/`, `data/`, `src/`, `tests/`) remains in place.
- Replaced/evolved: `README.md`, `docs/architecture.md`, and `docs/data-contracts.md` evolve from repository-establishment guidance into concrete inventory contract documentation.

## Cleanup
No external resources are created in this stage.
