# TinyWMS lesson: 12-concurrency

## Stage purpose
This stage shows why a naive order transaction can oversell stock when two requests overlap, then fixes that behavior with a visible database transaction guard. Students can run a small demo that prints the race before and after the fix, and they can compare the local SQLite proof with the real PostgreSQL row-lock lesson.

## Files in this lesson
- `deploy/local/run_local.sh` - starts the system on one machine, no AWS needed
- `src/local_aws.py` - configures local mode
- `tests/test_local_stack.py` - drives local mode over HTTP
- `README.md` - lesson guide for the concurrency demo, tests, and classroom exercises.
- `docs/architecture.md` - updated component map showing the hardening of the existing order/database path.
- `docs/data-contracts.md` - contract guide updated with the concurrency lesson note.
- `src/concurrency_demo.py` - student-facing demo that launches two overlapping orders and prints the outcomes.
- `src/lambda_inventory.py` - order implementation evolved to use a transaction strategy that prevents overselling.
- `tests/test_concurrency.py` - local concurrency proof using threads and a barrier.
- `tests/test_http_order_flow.py` - inherited HTTP order integration proof.
- `tests/test_lambda_inventory.py` - inherited Lambda contract tests.
- `tests/test_relational_persistence.py` - inherited relational persistence checks.
- `tests/test_sqlite_orders.py` - inherited SQLite transaction and rollback proofs.
- `tests/test_web_app.js` - inherited browser-contract safety check.

## Run it on your own machine
No AWS account needed. `GET /inventory` and `POST /orders` go through the same handler code Lambda runs, against a SQLite file instead of RDS:
```bash
bash deploy/local/run_local.sh            # add --reset to start from a clean database
# open http://127.0.0.1:8000/ , submit an order, and watch the quantities change
curl -s -H 'Content-Type: application/json' -d '{"order_id":"ORD-1","lines":[{"sku":"SKU-1001","quantity":1}]}' http://127.0.0.1:8000/orders
```
Setting `TINYWMS_LOCAL=1` is the only switch; it creates `local-aws/tinywms.db` on first start. A bad request returns 400, a shortage, unknown SKU or repeated `order_id` returns 409, and a rejected order changes nothing. SQLite locks the whole file, so it cannot show the row-lock lesson; that needs PostgreSQL.

## Run the lesson
From this folder:
```bash
python3 src/concurrency_demo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Edit the demo’s starting stock in `src/concurrency_demo.py` from 1 to 2, run `python3 src/concurrency_demo.py`, and compare how both overlapping order attempts now behave in the printed output.
2. Change the demo’s artificial delay or barrier timing, run `python3 src/concurrency_demo.py` again, and observe whether the second attempt still fails cleanly before optionally re-running the test suite.
## Continuity note
- Inherited contract: the inventory JSON contract, order JSON contract, browser page, local HTTP order path, Lambda order API, SQLite classroom path, and relational schema remain valid.
- Boundary changed in this stage: the order transaction now explicitly guards against concurrent overselling, and the lesson makes the PostgreSQL row-lock boundary visible.

## Component assembly update
- Added: `src/concurrency_demo.py` and `tests/test_concurrency.py` as the new concurrency lesson artifacts.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/orders.schema.json`, `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/order_form.html`, `src/sql_export.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `deploy/lambda/README.md`, `deploy/rds/README.md`, `tests/test_http_order_flow.py`, `tests/test_lambda_inventory.py`, `tests/test_relational_persistence.py`, `tests/test_sqlite_orders.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `src/lambda_inventory.py` now uses a clearer transaction strategy that prevents overselling when requests overlap.

## Cleanup
No external resources are created in this stage. If you created a temporary SQLite database or any local demo files, remove them when you are done.
