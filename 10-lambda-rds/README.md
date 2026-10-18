# TinyWMS lesson: 10-lambda-rds

## Stage purpose
This stage keeps the TinyWMS inventory contract stable while changing the Lambda implementation to read inventory from PostgreSQL/RDS instead of static JSON in the deployed path. Students can compare the unchanged JSON shape with the new database-backed compute path and still use the SQLite classroom path locally.

## Files in this lesson
- `deploy/local/run_local.sh` - starts the system on one machine, no AWS needed
- `src/local_aws.py` - configures local mode
- `tests/test_local_stack.py` - drives local mode over HTTP
- `data/.gitkeep` - keeps the `data/` directory present in a clean checkout.
- `data/init_db.py` - inherited module-form initializer for the relational schema and seed data.
- `data/inventory.json` - canonical inventory sample and contract input for the earlier stages.
- `data/inventory.schema.json` - JSON Schema for the inventory contract.
- `data/schema.sql` - relational inventory schema with `bin_location` as the SQL column name.
- `data/seed.sql` - seed rows derived from the inventory JSON sample.
- `deploy/api-gateway/README.md` - inherited API Gateway deployment notes used to resolve the Lambda front door.
- `deploy/ec2/README.md` - inherited EC2 runbook for the unchanged HTTP server path.
- `deploy/ec2/environment.example` - inherited environment example for the EC2 server.
- `deploy/ec2/run_inventory_server.sh` - inherited EC2 launcher for the HTTP server.
- `deploy/lambda/README.md` - inherited Lambda deployment notes for the compute boundary.
- `deploy/rds/README.md` - inherited RDS deployment notes for the database boundary.
- `docs/architecture.md` - updated component map showing Lambda’s data-source evolution from static JSON to RDS.
- `docs/data-contracts.md` - inherited contract guide describing the JSON-to-relational mapping.
- `infra/api-gateway.yaml` - inherited API Gateway template for the Lambda inventory path.
- `infra/lambda.yaml` - inherited Lambda template for the inventory lesson.
- `infra/rds.yaml` - inherited RDS template for the relational lesson.
- `src/.gitkeep` - keeps the `src/` directory present in a clean checkout.
- `src/db_adapter.py` - inherited narrow SQLite/PostgreSQL teaching adapter.
- `src/http_server.py` - inherited visible HTTP server for the direct Linux path.
- `src/inventory_cli.py` - inherited inventory CLI for list/find/dump exercises.
- `src/inventory_watcher.py` - inherited long-running file watcher.
- `src/lambda_inventory.py` - evolved Lambda inventory handler that reads from database rows.
- `src/linux_visible.py` - inherited Linux visibility helper.
- `src/sql_export.py` - inherited JSON-to-SQL export helper.
- `src/web/app.js` - inherited browser client that fetches `GET /inventory`.
- `src/web/index.html` - inherited browser page.
- `src/web/style.css` - inherited browser styling.
- `tests/.gitkeep` - keeps the `tests/` directory present in a clean checkout.
- `tests/test_http_server.py` - inherited HTTP contract tests.
- `tests/test_inventory_cli.py` - inherited CLI contract tests.
- `tests/test_inventory_watcher.py` - inherited watcher tests.
- `tests/test_linux_visible.py` - inherited Linux visibility tests.
- `tests/test_lambda_inventory.py` - evolved Lambda inventory tests that inject a fake database connection.
- `tests/test_relational_persistence.py` - inherited relational persistence tests.
- `tests/test_web_app.js` - inherited Node safety check for the browser contract.

## Run it on your own machine
No AWS account needed. The same handler code Lambda runs answers the page, reading rows from a SQLite file instead of RDS:
```bash
bash deploy/local/run_local.sh            # add --reset to start from a clean database
# open http://127.0.0.1:8000/
```
Setting `TINYWMS_LOCAL=1` is the only switch; `deploy/local/run_local.sh` sets it for you and creates `local-aws/tinywms.db` from `data/schema.sql` and `data/seed.sql` on first start.

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
1. Change one quantity in `data/inventory.json`, rerun `python3 -m data.init_db` for the SQLite path, and use `python3 -m unittest tests.test_lambda_inventory -v` or `curl` against the local HTTP path to compare the old sample with the database-backed result.
2. Edit `tests/test_lambda_inventory.py` so the fake database row returns a different `bin_location`, then observe the changed behavior through the lesson's visible interface, then optionally run the tests and observe the returned JSON field still named `bin_location`.
## Continuity note
- Inherited contract: the inventory JSON fields, JSON Schema, CLI, Linux-visible helper scripts, HTTP `/inventory` response, browser inventory page, EC2 deployment wrapper, API Gateway front door, relational schema, and RDS deployment wrapper all remain valid.
- Boundary changed in this stage: Lambda’s deployed inventory path now opens a PostgreSQL connection and reads inventory rows from the database instead of returning only static JSON.

## Component assembly update
- Added: `src/lambda_inventory.py` now contains the database-backed Lambda inventory path for Stage 10.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/db_adapter.py`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/sql_export.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `deploy/lambda/README.md`, `deploy/rds/README.md`, `infra/api-gateway.yaml`, `infra/lambda.yaml`, `infra/rds.yaml`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_relational_persistence.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `src/lambda_inventory.py` and `tests/test_lambda_inventory.py` now demonstrate the Lambda-to-RDS data-source shift while preserving the established inventory JSON contract.

## Cleanup
No external resources are created in this stage. If you created a local SQLite database while exercising the lesson, remove `data/tinywms.db` when you are done.
