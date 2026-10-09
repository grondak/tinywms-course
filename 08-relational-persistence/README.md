# TinyWMS lesson: 08-relational-persistence

## Stage purpose
This stage introduces a small relational database version of TinyWMS inventory without changing the existing HTTP, Lambda, or browser contracts. Students can compare the original JSON document with a relational schema and see exactly how the fields map into tables.

## Files in this lesson
- `data/inventory.json` - the original JSON sample inventory that still serves as the source of truth for the lesson
- `data/schema.sql` - SQL schema for the relational inventory model
- `data/seed.sql` - seed data that loads the sample products into tables
- `data/load_from_json.py` - simple loader that converts the JSON sample into SQL `INSERT` statements
- `docs/architecture.md` - records that the system now has a relational persistence option alongside the earlier JSON-only flow
- `docs/data-contracts.md` - documents the JSON-to-table mapping for products and inventory rows
- `src/relational_inventory.py` - small Python helper for reading inventory rows from a relational database
- `tests/test_relational_inventory.py` - tests for schema mapping and query helpers

## Run the lesson
From this folder:
```bash
python3 data/load_from_json.py data/inventory.json
python3 src/relational_inventory.py --help
```
To experiment with a local PostgreSQL or MariaDB database, create the schema with `data/schema.sql`, load `data/seed.sql`, and point the helper at the database using environment variables documented in the script.

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Add a new inventory item to `data/inventory.json`, regenerate the seed output, and verify the relational rows still match the JSON contract.
2. Change the schema to split `quantity` into `on_hand` and `reserved`, then update the docs and tests to explain how the JSON contract maps to the new columns.

## Continuity note
- Inherited contract: the inventory JSON document and its field meanings remain the same as earlier stages
- Boundary changed in this stage: data can now live in a relational database and the JSON inventory is mapped into tables instead of being stored only as a file

## Cleanup
No external resources are created by the local scripts. If you start a database process for class, stop it with your normal Linux service or process commands and delete any temporary database files or containers you created.
