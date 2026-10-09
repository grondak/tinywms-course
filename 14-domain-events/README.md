# TinyWMS lesson: 14-domain-events

## Stage purpose
This stage introduces a domain event named `OrderPlaced` that is separate from the existing imperative SQS pick-work command. After a successful committed order, TinyWMS now says both "this happened" through Amazon EventBridge and "do this" through Amazon SQS so students can compare event-driven consumers with command-driven workers.

## Files in this lesson
- `src/order_service.py` - order handler now publishes both the existing SQS pick-work command and a new EventBridge domain event after commit
- `src/domain_events.py` - defines the versioned `OrderPlaced` event contract and a small command-line viewer for event JSON
- `src/eventbridge_publish.py` - visible EventBridge publisher using environment variables and explicit JSON payloads
- `src/event_consumer_shipping.py` - first independent event consumer that prints a shipping-style reaction to `OrderPlaced`
- `src/event_consumer_audit.py` - second independent event consumer that prints an audit-style reaction to `OrderPlaced`
- `data/order-placed-event-example.json` - example domain event students can inspect and replay locally
- `docs/data-contracts.md` - documents the distinction between the `OrderPlaced` event and the `PickWorkRequested` command
- `docs/architecture.md` - explains the new event boundary and the independent consumers
- `deploy/events/template.json` - minimal CloudFormation for a teaching EventBridge bus and two rules
- `deploy/events/publish-example.sh` - publishes the example `OrderPlaced` event to EventBridge
- `deploy/events/run-shipping-consumer.sh` - runs the shipping consumer locally against example JSON
- `deploy/events/run-audit-consumer.sh` - runs the audit consumer locally against example JSON
- `tests/test_domain_events.py` - tests the event contract built from a committed order result
- `tests/test_eventbridge_publish.py` - tests visible EventBridge publishing behavior without calling AWS
- `tests/test_event_consumers.py` - tests both independent consumers against the same event input
- `tests/test_order_service.py` - now checks that the order path can publish both a command and a domain event

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
python3 -m src.domain_events < data/order-placed-event-example.json
python3 src/event_consumer_shipping.py < data/order-placed-event-example.json
python3 src/event_consumer_audit.py < data/order-placed-event-example.json
```

To publish a real `OrderPlaced` event after creating an order through Lambda, set these environment variables before invoking the order path:
```bash
export TINYWMS_DB_HOST=127.0.0.1
export TINYWMS_DB_PORT=5432
export TINYWMS_DB_NAME=tinywms
export TINYWMS_DB_USER=tinywms
export TINYWMS_DB_PASSWORD=secret
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export TINYWMS_EVENT_BUS_NAME=default
export AWS_REGION=us-east-1
python3 src/lambda_inventory.py < src/order_event_example.json
```
The order response still comes back after the database commit. The pick-work command goes to SQS, while the new `OrderPlaced` event goes to EventBridge.

To publish the example event directly:
```bash
export TINYWMS_EVENT_BUS_NAME=default
export AWS_REGION=us-east-1
python3 src/eventbridge_publish.py data/order-placed-event-example.json
```

To run both local consumers independently against the same event:
```bash
python3 src/event_consumer_shipping.py < data/order-placed-event-example.json
python3 src/event_consumer_audit.py < data/order-placed-event-example.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Add a new field such as `sourceSystem` to `OrderPlaced` in `src/domain_events.py`, update `data/order-placed-event-example.json`, document it in `docs/data-contracts.md`, and re-run the tests.
2. Modify one consumer, such as `src/event_consumer_audit.py`, to print a different summary format. Re-run `tests/test_event_consumers.py` and confirm the other consumer did not need any code change.

## Continuity note
- Inherited contract: `GET /inventory`, `POST /orders`, the order request/response JSON, and the existing SQS `PickWorkRequested` message all remain valid
- Boundary changed in this stage: after a successful order commit, TinyWMS now also publishes a separate `OrderPlaced` domain event to Amazon EventBridge so independent consumers can react to what happened without being coupled to the order Lambda

## Cleanup
Local automated tests do not create AWS resources. If you deploy the EventBridge stack, delete it when finished:
```bash
aws cloudformation delete-stack --stack-name tinywms-events
```
If you also created the earlier SQS stack, delete that too when you are done with the lab:
```bash
aws cloudformation delete-stack --stack-name tinywms-sqs
```
Also unset environment variables containing database, queue, or event-bus settings when you leave a shared shell.
