# TinyWMS lesson: 14-domain-events

## Stage purpose
This stage separates two ideas that were previously combined: the imperative pick-work command sent to SQS and the factual `OrderPlaced` event sent to EventBridge. Students can compare "do this next" with "this happened" while keeping the existing order transaction, queue command, and inventory contract intact.

## Files in this lesson
- `README.md` - lesson guide for the event boundary, consumer demos, and compatibility checks.
- `docs/architecture.md` - updated component map and stage history showing the new event path beside the existing queue path.
- `docs/data-contracts.md` - updated contract guide with the `OrderPlaced` event shape and its relation to the queue command.
- `deploy/events/README.md` - deploy/resolve/verify/destroy commands for the EventBridge lesson.
- `infra/events.yaml` - CloudFormation template for the event bus, two rules, two queues, and queue policies.
- `src/event_consumer_a.py` - independent consumer for target queue A.
- `src/event_consumer_b.py` - independent consumer for target queue B.
- `src/lambda_inventory.py` - order handler evolved to publish both the SQS pick-work command and the EventBridge `OrderPlaced` event after commit.
- `tests/test_concurrency.py` - updated concurrency proof that injects both queue and event clients.
- `tests/test_lambda_inventory.py` - updated order-handler contract tests for both async payloads.
- `tests/test_event_consumers.py` - local tests for the two independent EventBridge consumers.
- `tests/test_sqs_consumer.py` - inherited queue consumer tests that still prove receive/delete semantics.
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
1. Edit the `detail-type` or `source` fields in `src/lambda_inventory.py`, then observe the changed behavior through the lesson's visible interface, then optionally run the tests to observe how the visible JSON event shape changes while the pick-work command stays separate.
2. Change the filter pattern in `infra/events.yaml` for one rule, redeploy the template, and inspect which queue receives the event first using the AWS CLI or the small Python consumer scripts.
## Continuity note
- Inherited contract: the inventory JSON contract, order JSON contract, pick-work command contract, HTTP order path, browser order page, SQLite classroom path, and SQS consumer behavior remain valid.
- Boundary changed in this stage: after commit, the order path now emits a factual EventBridge event in addition to the existing queue command, and the event is fanned out to two independent consumer queues.

## Component assembly update
- Added: `infra/events.yaml`, `deploy/events/README.md`, `src/event_consumer_a.py`, `src/event_consumer_b.py`, and `tests/test_event_consumers.py` as the new event lesson artifacts.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/orders.schema.json`, `data/pick-work.json`, `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/order_form.html`, `src/sql_export.py`, `src/sqs_consumer.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `deploy/api-gateway/README.md`, `deploy/lambda/README.md`, `deploy/rds/README.md`, `deploy/sqs/README.md`, `infra/api-gateway.yaml`, `infra/lambda.yaml`, `infra/rds.yaml`, `infra/sqs.yaml`, `tests/test_http_order_flow.py`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_relational_persistence.py`, `tests/test_sqlite_orders.py`, `tests/test_sqs_consumer.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `src/lambda_inventory.py`, `tests/test_concurrency.py`, and `tests/test_lambda_inventory.py` now publish an `OrderPlaced` event after commit while preserving the SQS command path.

## Cleanup
No external resources are created by the Python tests. If you deploy the event lesson, destroy the CloudFormation stack when you are done.
