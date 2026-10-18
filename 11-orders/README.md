# TinyWMS lesson: 11-orders

## Stage purpose
This stage adds the first write path to TinyWMS. Students can submit a small JSON order, watch the server validate and commit it inside a database transaction, and then see the inventory quantity change through the same visible HTTP and browser contracts used earlier.

## Files in this lesson
- `data/.gitkeep` - keeps the `data/` directory present in a clean checkout.
- `data/init_db.py` - inherited module-form initializer for the relational schema and seed data.
- `data/inventory.json` - canonical inventory sample and contract input for earlier stages.
- `data/inventory.schema.json` - JSON Schema for the inventory contract.
- `data/orders.schema.json` - new JSON Schema for the order contract.
- `data/schema.sql` - evolved relational schema that adds `orders` and `order_lines`.
- `data/seed.sql` - seed rows derived from the inventory JSON sample.
- `deploy/api-gateway/README.md` - inherited deployment notes for the Lambda front door.
- `deploy/ec2/README.md` - inherited EC2 runbook for the unchanged HTTP server path.
- `deploy/ec2/environment.example` - inherited environment example for the EC2 server.
- `deploy/ec2/run_inventory_server.sh` - inherited EC2 launcher for the HTTP server.
- `deploy/lambda/README.md` - inherited Lambda deployment notes.
- `deploy/rds/README.md` - inherited RDS deployment notes.
- `docs/architecture.md` - component map and evolution notes for the order lesson.
- `docs/data-contracts.md` - contract guide that now documents order JSON and the order tables.
- `src/http_server.py` - local HTTP server that now serves the browser assets and accepts `POST /orders`.
- `src/lambda_inventory.py` - Lambda handler evolved to validate and commit orders transactionally.
- `src/order_form.html` - preserved standalone order form for historical comparison.
- `src/web/app.js` - browser app evolved into the integrated inventory-and-order workflow.
- `src/web/index.html` - integrated browser page that shows inventory, order JSON, and response JSON.
- `src/web/style.css` - shared browser styling.
- `tests/test_http_order_flow.py` - local HTTP integration proof for order submission and refreshed inventory.
- `tests/test_sqlite_orders.py` - SQLite-backed order transaction tests using the real initializer and adapter.
- `tests/test_http_server.py` - inherited HTTP contract tests for `GET /inventory`.
- `tests/test_inventory_cli.py` - inherited CLI contract tests.
- `tests/test_inventory_watcher.py` - inherited watcher tests.
- `tests/test_linux_visible.py` - inherited Linux visibility tests.
- `tests/test_lambda_inventory.py` - inherited Lambda inventory tests.
- `tests/test_relational_persistence.py` - inherited relational persistence tests.
- `tests/test_web_app.js` - Node safety check for the browser contract.

## Run the lesson
From this folder:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m data.init_db
python3 src/http_server.py
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Change the default quantity or SKU in `src/web/app.js`, run the local HTTP server, and submit an order from the browser while watching the inventory table refresh after acceptance.
2. Edit `tests/test_http_order_flow.py` so the temporary order requests two units instead of one, then observe the changed on-disk inventory response through the HTTP endpoint before optionally re-running the test suite.
## Continuity note
- Inherited contract: the inventory JSON fields, inventory schema, CLI, Linux-visible tools, `GET /inventory`, browser inventory page, EC2 deployment wrapper, Lambda inventory path, API Gateway front door, and the SQLite/PostgreSQL relational path remain valid.
- Boundary changed in this stage: the local HTTP server and Lambda handler now accept `POST /orders`, validate the request, write order rows, decrement inventory, and return visible order JSON.

## Component assembly update
- Added: `data/orders.schema.json`, `tests/test_http_order_flow.py`, `tests/test_sqlite_orders.py`, and the integrated order workflow in `src/http_server.py`, `src/lambda_inventory.py`, `src/web/index.html`, and `src/web/app.js`.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/init_db.py`, `data/seed.sql`, `src/order_form.html`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `deploy/lambda/README.md`, `deploy/rds/README.md`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_lambda_inventory.py`, `tests/test_relational_persistence.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `data/schema.sql`, `src/http_server.py`, `src/lambda_inventory.py`, `src/web/index.html`, and `src/web/app.js` now support transactional order placement while preserving the earlier inventory contract.

## Cleanup
No external resources are created in this stage. If you created a local SQLite database while exercising the lesson, remove `data/tinywms.db` when you are done.
