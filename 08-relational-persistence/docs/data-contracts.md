# TinyWMS Data Contracts

This document describes the TinyWMS inventory JSON contract and how Stage 8 maps that contract into relational structures.

## Inventory JSON

Inventory is stored as a JSON array of objects. Each object represents one stock item and is reused by the CLI, the Linux demo tools, the HTTP server, the browser page, the EC2 deployment wrapper, and the Lambda handler.

### Fields
- `sku` - unique stock keeping unit string used to identify the item.
- `description` - human-readable item description.
- `bin_location` - warehouse bin identifier where the item is stored.
- `quantity` - on-hand count stored as a non-negative integer.
- `unit` - quantity unit string such as `each` or `roll`.

### Notes
- The CLI validates that these required fields are present before it lists or finds items.
- The HTTP server returns this same JSON structure unchanged at `GET /inventory`.
- The browser page fetches the same JSON structure and renders it as a table.
- The EC2 deployment wrapper does not change the JSON contract; it only changes where the same HTTP process is started.
- The Lambda handler returns the same inventory JSON contract from a different compute boundary.
- The JSON file remains the canonical interchange format for this stage.

## Relational mapping introduced in Stage 8

Stage 8 introduces a minimal relational representation for the existing inventory JSON data. The mapping is intentionally one-to-one so students can compare the two forms without extra abstraction.

### Table: `inventory`
- `sku TEXT PRIMARY KEY` - maps from `sku`.
- `description TEXT NOT NULL` - maps from `description`.
- `bin_location TEXT NOT NULL` - maps from `bin_location`.
- `quantity INTEGER NOT NULL CHECK (quantity >= 0)` - maps from `quantity`.
- `unit TEXT NOT NULL` - maps from `unit`.

### Seed source
The seed script is derived from `data/inventory.json` and loads the same sample rows into the relational table. The row values should match the JSON file exactly so students can compare file output, SQL inserts, and database contents.

### Database selection
- `TINYWMS_DB=sqlite` selects the local classroom path.
- `TINYWMS_DB=postgres` selects the PostgreSQL path and remains the default.
- `TINYWMS_SQLITE_PATH` chooses the SQLite database file when the SQLite path is selected.

### Teaching note
SQLite is used here to make the lesson runnable on a student laptop, but it is still a local file-backed database. It does not demonstrate a separate database server process, network port, or row-locking behavior. PostgreSQL remains the path for instructor demonstrations of the later operational lessons.
