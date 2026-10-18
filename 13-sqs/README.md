# TinyWMS lesson: 13-sqs

## Stage purpose
This stage adds the first asynchronous boundary to TinyWMS: after an order commits, the system publishes one pick-work command per order line to SQS. Students can compare the synchronous order transaction from Stage 12 with the new queue handoff and inspect the JSON command shape directly.

## Files in this lesson
- `README.md` - lesson guide for the SQS handoff, local consumer helper, and continuity checks.
- `docs/architecture.md` - updated component map showing the queue boundary and the new consumer role.
- `docs/data-contracts.md` - updated contract guide with the pick-work command shape.
- `data/pick-work.json` - visible example of the pick-work command JSON contract.
- `deploy/sqs/README.md` - queue deployment notes with exact deploy, resolve, verify, and destroy commands.
- `infra/sqs.yaml` - minimal CloudFormation template for the pick-work queue.
- `src/lambda_inventory.py` - order path evolved to publish pick-work commands after commit.
- `src/sqs_consumer.py` - small SQS consumer helper that long-polls once, decodes message JSON, and deletes only after success.
- `tests/test_concurrency.py` - concurrency proof updated to inject a fake SQS client and prove rollback never publishes.
- `tests/test_lambda_inventory.py` - Lambda contract tests updated for the queue publish boundary.
- `tests/test_sqs_consumer.py` - local consumer tests for receive, delete, failure, and multi-message behavior.
- `tests/test_web_app.js` - inherited browser-contract safety check.

## Run the lesson
From this folder:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Change the queue command body in `src/lambda_inventory.py` to include a temporary note field, observe the changed behavior through the lesson's visible interface, then optionally run the tests or a small injected fake SQS client, and inspect the exact JSON sent to the fake SQS client in the visible test output.
2. Edit the consumer callback in `tests/test_sqs_consumer.py` so it raises on one message, observe the changed behavior through the lesson's visible interface, then optionally run the tests, and observe that the message is left undeleted while the successful message still gets acknowledged.
## Continuity note
- Inherited contract: the inventory JSON contract, order JSON contract, HTTP order path, browser order page, SQLite classroom path, and Stage 12 concurrency guard remain valid.
- Boundary changed in this stage: the committed order path now crosses a queue boundary before pick-ticket work begins, and the consumer processes SQS messages one poll at a time.

## Component assembly update
- Added: `data/pick-work.json`, `infra/sqs.yaml`, `deploy/sqs/README.md`, and `src/sqs_consumer.py` as the new queue and consumer lesson artifacts.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/orders.schema.json`, `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/order_form.html`, `src/sql_export.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `deploy/lambda/README.md`, `deploy/rds/README.md`, `infra/api-gateway.yaml`, `infra/lambda.yaml`, `infra/rds.yaml`, `tests/test_http_order_flow.py`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_relational_persistence.py`, `tests/test_sqlite_orders.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `src/lambda_inventory.py`, `tests/test_concurrency.py`, and `tests/test_lambda_inventory.py` now prove the order path commits before any queue publish and that rollback never sends messages.

## Cleanup
No external resources are created by the Python tests. If you deploy the queue lesson, destroy the CloudFormation stack when you are done.
