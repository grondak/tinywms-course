# TinyWMS lesson: 09-rds

## Stage purpose
This stage keeps the Stage 8 relational inventory lesson intact and adds a managed Amazon RDS deployment option for the PostgreSQL path. Students can now compare a self-managed Linux database with AWS-managed RDS while the local SQLite classroom path remains available.

## Files in this lesson
- `data/init_db.py` - inherited module-form initializer that still creates the relational schema and loads seed data.
- `data/inventory.json` - inherited canonical inventory sample that still defines the inventory contract.
- `data/inventory.schema.json` - inherited JSON Schema for the inventory contract.
- `data/schema.sql` - inherited inventory table definition with `bin_location` as the canonical relational column.
- `data/seed.sql` - inherited seed rows derived from the inventory JSON sample.
- `deploy/rds/README.md` - new operator guide for deploying and verifying the RDS lesson.
- `docs/architecture.md` - updated component map showing the managed RDS hosting boundary.
- `docs/data-contracts.md` - updated contract notes comparing SQLite, PostgreSQL, and RDS responsibilities.
- `infra/rds.yaml` - new CloudFormation template for the lesson-scale RDS deployment.
- `src/db_adapter.py` - inherited narrow SQLite/PostgreSQL teaching adapter.
- `src/http_server.py` - inherited transparent HTTP server that still serves `/inventory` from the same contract.
- `src/inventory_cli.py` - inherited CLI for listing and finding inventory.
- `src/inventory_watcher.py` - inherited long-running file/process watcher.
- `src/linux_visible.py` - inherited Linux visibility helper.
- `src/lambda_inventory.py` - inherited Lambda inventory handler.
- `src/sql_export.py` - inherited JSON-to-SQL export helper.
- `src/web/app.js` - inherited browser client that fetches `GET /inventory`.
- `src/web/index.html` - inherited browser page.
- `src/web/style.css` - inherited browser styling.
- `tests/test_http_server.py` - inherited HTTP contract tests.
- `tests/test_inventory_cli.py` - inherited CLI contract tests.
- `tests/test_inventory_watcher.py` - inherited watcher tests.
- `tests/test_linux_visible.py` - inherited Linux visibility tests.
- `tests/test_lambda_inventory.py` - inherited Lambda inventory tests.
- `tests/test_relational_persistence.py` - inherited relational persistence tests for schema, seed, adapter, and SQLite bootstrap.
- `tests/test_web_app.js` - inherited Node safety check for the browser contract.

## Run the lesson
From this folder:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m data.init_db
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Read `deploy/rds/README.md`, then compare the RDS parameter names with the `DatabaseEndpoint` and `DatabasePort` environment variables already used by the later Lambda path in the course.
2. Edit `data/seed.sql` to change one quantity, rerun `TINYWMS_DB=sqlite TINYWMS_SQLITE_PATH=data/tinywms.db python3 -m data.init_db`, and query the resulting SQLite database to see the updated row before comparing that same schema to the RDS template.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible tools, HTTP `/inventory` response, browser inventory page, EC2 deployment wrapper, Lambda inventory handler, and relational schema/initializer remain valid.
- Boundary changed in this stage: the lesson adds managed RDS as the PostgreSQL hosting option and makes the operational difference between self-managed Linux database handling and AWS-managed database operations visible.

## Component assembly update
- Added: `infra/rds.yaml` and `deploy/rds/README.md` as the new RDS deployment wrapper for the relational lesson.
- Reused unchanged: `data/init_db.py`, `data/schema.sql`, `data/seed.sql`, `src/db_adapter.py`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/lambda_inventory.py`, `src/sql_export.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_lambda_inventory.py`, `tests/test_relational_persistence.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `README.md`, `docs/architecture.md`, and `docs/data-contracts.md` now document the managed RDS boundary, including how the same SQL schema is hosted differently without changing the inventory contract.

## Cleanup
Destroy the RDS stack when you are done:
```bash
aws cloudformation delete-stack --stack-name tinywms-rds
```
If you created a local SQLite database for practice, delete `data/tinywms.db` as well.
