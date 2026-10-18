# TinyWMS lesson: 08-relational-persistence

## Stage purpose
This stage maps the existing inventory JSON model into a minimal relational schema so students can see how the same warehouse data moves from a JSON file into SQL tables. The lesson keeps the inventory-only scope on purpose: orders and order lines come later.

## Files in this lesson
- `data/init_db.py` - module-form database initializer that loads the schema and seed data through the teaching adapter.
- `data/inventory.json` - reused canonical inventory sample that still defines the visible inventory contract.
- `data/inventory.schema.json` - reused JSON Schema for the inventory contract.
- `data/schema.sql` - inventory table definition for the relational lesson.
- `data/seed.sql` - seed rows derived from the existing inventory JSON sample.
- `deploy/api-gateway/README.md` - reused API Gateway deployment guide from the prior stage.
- `deploy/ec2/README.md` - reused EC2 deployment guide for the direct HTTP path.
- `deploy/ec2/environment.example` - reused EC2 environment sample.
- `deploy/ec2/run_inventory_server.sh` - reused EC2 startup wrapper.
- `docs/architecture.md` - updated component map showing the relational schema and initializer.
- `docs/data-contracts.md` - updated data-contract notes describing the JSON-to-SQL mapping.
- `src/db_adapter.py` - narrow SQLite/PostgreSQL teaching adapter.
- `src/http_server.py` - reused direct HTTP server for the Pi/EC2 path.
- `src/inventory_cli.py` - reused CLI for listing and finding inventory.
- `src/inventory_watcher.py` - reused long-running file/process watcher.
- `src/linux_visible.py` - reused Linux visibility helper.
- `src/lambda_inventory.py` - reused Lambda inventory handler from the prior stage.
- `src/sql_export.py` - JSON-to-SQL export helper for the seed lesson.
- `src/web/app.js` - reused browser client that still fetches the same inventory contract.
- `src/web/index.html` - reused browser page.
- `src/web/style.css` - reused browser styling.
- `tests/test_http_server.py` - reused HTTP contract tests.
- `tests/test_inventory_cli.py` - reused CLI contract tests.
- `tests/test_inventory_watcher.py` - reused watcher tests.
- `tests/test_linux_visible.py` - reused Linux visibility tests.
- `tests/test_lambda_inventory.py` - reused Lambda inventory tests.
- `tests/test_relational_persistence.py` - new relational persistence tests for schema, seed, adapter, and initializer behavior.
- `tests/test_web_app.js` - reused Node safety check for the browser contract.

## Run the lesson
From this folder:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
TINYWMS_DB=sqlite TINYWMS_SQLITE_PATH=data/tinywms.db python3 -m data.init_db
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Run the initializer, then open the SQLite database with a local SQL client and inspect the `inventory` table to compare the column names with the keys in `data/inventory.json`.
2. Edit `data/seed.sql` to change one quantity, rerun `TINYWMS_DB=sqlite TINYWMS_SQLITE_PATH=data/tinywms.db python3 -m data.init_db`, and then query the database again to see the changed row.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible helpers, direct HTTP `/inventory` response, browser inventory page, EC2 deployment wrapper, Lambda inventory handler, and API Gateway front door remain valid and unchanged.
- Boundary changed in this stage: the lesson adds a visible relational persistence boundary with SQL schema, seed, and database initialization while leaving the running application paths on the existing inventory JSON contract.

## Component assembly update
- Added: `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/db_adapter.py`, `src/sql_export.py`, and `tests/test_relational_persistence.py` as the first relational persistence teaching components.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/lambda_inventory.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_lambda_inventory.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `docs/architecture.md` and `docs/data-contracts.md` now document how the JSON inventory fields map into a relational inventory table and how the initializer loads the same sample data.

## Cleanup
No external resources are created in this stage. If you create a local SQLite database file with the initializer, delete `data/tinywms.db` when you are finished.
