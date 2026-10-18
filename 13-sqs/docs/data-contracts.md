# TinyWMS Data Contracts

This document describes the TinyWMS inventory JSON contract, the order JSON contract introduced in Stage 11, the pick-work command contract introduced in Stage 13, and how the existing relational persistence maps those contracts into tables.

SQLite cannot demonstrate the PostgreSQL row-lock lesson.

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

## Order JSON

Stage 11 introduces a minimal order contract for submitting warehouse orders.

### Fields
- `order_id` - unique order identifier string.
- `lines` - non-empty array of order line objects.

### Order line fields
- `sku` - inventory SKU to decrement.
- `quantity` - positive integer quantity to reserve.
- `description` - optional human-readable description carried by the browser and handler for visibility.

### Notes
- The browser sends visible JSON to `POST /orders` and shows the request and response JSON.
- The local HTTP server validates order JSON, writes orders and order lines in a transaction, decrements inventory, and returns accepted/rejected JSON.
- The Lambda handler uses the same request/response contract so the deployed HTTP path can remain stable.
- Stage 12 keeps the same order JSON contract and tightens the transaction boundary so concurrent attempts cannot oversell inventory.

## Pick-work command JSON

Stage 13 adds a queue message contract that represents work to be done after an order commits.

### Fields
- `command_id` - stable versioned command identifier derived from the order, SKU, quantity, and bin.
- `order_id` - order identifier that triggered the command.
- `sku` - inventory SKU to pick.
- `description` - description copied from the locked inventory row.
- `quantity` - positive integer quantity to pick.
- `bin` - bin location copied from the locked inventory row.

### Notes
- The command is published after the order transaction commits.
- One command is produced for each order line.
- The downstream consumer receives the decoded JSON body, not the SQS envelope.
- The queue boundary exists so the order path does not block on pick-ticket generation.
- The bin field is intentionally a visible queue-field name, while the database column remains `bin_location`.

## Relational mapping introduced in Stage 8

Stage 8 introduces a minimal relational representation for the existing inventory JSON data. The mapping is intentionally one-to-one so students can compare the two forms without extra abstraction.

### Table: `inventory`
- `sku TEXT PRIMARY KEY` - maps from `sku`.
- `description TEXT NOT NULL` - maps from `description`.
- `bin_location TEXT NOT NULL` - maps from `bin_location`.
- `quantity INTEGER NOT NULL CHECK (quantity >= 0)` - maps from `quantity`.
- `unit TEXT NOT NULL` - maps from `unit`.

### Table: `orders`
- `order_id TEXT PRIMARY KEY` - maps from `order_id`.
- `status TEXT NOT NULL` - visible order state such as `accepted`.

### Table: `order_lines`
- `order_id TEXT NOT NULL` - references `orders.order_id`.
- `sku TEXT NOT NULL` - references `inventory.sku`.
- `quantity INTEGER NOT NULL CHECK (quantity > 0)` - maps from the submitted line quantity.

### Seed source
The seed script is derived from `data/inventory.json` and loads the same sample rows into the relational table. The row values should match the JSON file exactly so students can compare file output, SQL inserts, and database contents.

### Database selection
- `TINYWMS_DB=sqlite` selects the local classroom path.
- `TINYWMS_DB=postgres` selects the PostgreSQL path and remains the default.
- `TINYWMS_SQLITE_PATH` chooses the SQLite database file when the SQLite path is selected.

### Stage 9 RDS note
RDS does not change the logical schema. It changes who operates the PostgreSQL server and where the endpoint comes from.

- In the self-managed Linux path, students and instructors are responsible for installing, starting, securing, and stopping the database process.
- In the RDS path, AWS operates the database process, storage, backups, endpoint lifecycle, and patching responsibilities within the scope of the lesson.
- The application still speaks the same SQL schema and reads the same visible relational columns.

### Stage 12 concurrency note
Stage 12 demonstrates why overlapping order attempts need a transaction strategy that prevents overselling. The lesson uses a concurrency demo plus database assertions to show that only one order can consume the final unit of stock.

- SQLite remains useful for transaction smoke tests and rollback proofs.
- PostgreSQL is the path for the real row-lock lesson, because the concurrency boundary is visible there with `SELECT ... FOR UPDATE` or an equivalent atomic quantity guard.
- SQLite cannot demonstrate the PostgreSQL row-lock lesson.

### Teaching note
SQLite is used here to make the lesson runnable on a student laptop, but it is still a local file-backed database. It does not demonstrate a separate database server process, network port, or row-locking behavior. PostgreSQL remains the path for instructor demonstrations of the later operational lessons, and RDS is the managed hosting version of that PostgreSQL path.
