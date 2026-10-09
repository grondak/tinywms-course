# TinyWMS lesson: 12-concurrency

## Stage purpose
This stage makes a distributed-systems problem visible inside a tiny warehouse application: two order attempts can race for the same last unit of stock. Students first reproduce the naive oversell, then inspect the smallest understandable SQL transaction strategy that prevents it without hiding the database boundary.

## Files in this lesson
- `src/rds_inventory.py` - order write path changed from separate read-then-update logic to a conditional decrement statement that keeps the transaction boundary visible in SQL
- `src/concurrency_demo.py` - local threaded demonstration script with an explicit naive race and a fixed version using the same order contract shape
- `docs/architecture.md` - explains what changed about concurrent order handling and why the transaction strategy matters
- `docs/data-contracts.md` - documents that order failure semantics now include contention-safe inventory checks with the same JSON response contract
- `tests/test_rds_inventory.py` - expanded tests showing the fixed SQL strategy prevents overselling and still rolls back cleanly
- `tests/test_concurrency_demo.py` - tests that make the naive race reproducible and verify the fixed path allows only one winner
- `data/schema.sql` - schema comments updated for the concurrency lesson while preserving table meaning
- `deploy/rds/bootstrap.sql` - bootstrap SQL comments updated so deployed databases match the lesson documentation

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
python3 src/concurrency_demo.py naive
python3 src/concurrency_demo.py fixed
TINYWMS_DB_HOST=127.0.0.1 TINYWMS_DB_PORT=5432 TINYWMS_DB_NAME=tinywms TINYWMS_DB_USER=tinywms TINYWMS_DB_PASSWORD=secret python3 src/lambda_inventory.py < src/order_event_example.json
```
The `naive` demo uses two threads and a SQLite database file to show how two workers can both read the same quantity before either writes it back. The `fixed` demo uses the TinyWMS order logic with a conditional SQL decrement so only one order can commit when one unit remains.

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `src/concurrency_demo.py` to change the starting quantity from `1` to `2`. Re-run both demo modes and explain why the before/after outcomes differ.
2. In `tests/test_rds_inventory.py`, add a case where two concurrent orders each request `2` units from a starting quantity of `3`. Re-run the suite and verify that exactly one order succeeds.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same JSON, and `POST /orders` still accepts the same request body and returns the same success and failure JSON shapes
- Boundary changed in this stage: the database write strategy for `POST /orders` now explicitly handles concurrent attempts to consume the same inventory so the same HTTP contract remains correct under contention

## Cleanup
No external resources are created by the automated tests. The concurrency demo creates a temporary SQLite database file and deletes it automatically. If you run against deployed AWS resources, clean up Lambda, API Gateway, RDS, related security groups, subnet groups, and logs when finished to avoid charges.
