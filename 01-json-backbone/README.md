# TinyWMS lesson: 01-json-backbone

## Stage purpose
This stage defines TinyWMS inventory as readable JSON and introduces a tiny Python CLI that can inspect and validate that JSON. The goal is to make the contract visible before any HTTP server, browser, or database appears.

## Files in this lesson
- `data/inventory.json` - sample warehouse inventory in the canonical JSON format
- `data/inventory.schema.json` - JSON Schema describing the inventory document
- `docs/data-contracts.md` - field-by-field explanation of the inventory contract
- `src/inventory_cli.py` - small Python tool to list inventory, find a SKU, validate required fields, and emit JSON
- `tests/test_inventory_cli.py` - tests for contract loading and CLI behavior
- `docs/architecture.md` - still records the repository’s current simple architecture

## Run the lesson
From this folder:
```bash
python3 src/inventory_cli.py list data/inventory.json
python3 src/inventory_cli.py find data/inventory.json SKU-1002
python3 src/inventory_cli.py emit data/inventory.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Add one more product to `data/inventory.json` and re-run `list` and the tests.
2. Change the lookup SKU in `find` to a missing value and observe the exit code and error message.

## Continuity note
- Inherited contract: the repository structure and the promise that JSON will be the canonical interchange format
- Boundary changed in this stage: the first concrete inventory JSON document and a CLI boundary were added

## Cleanup
No external resources are created in this stage.
