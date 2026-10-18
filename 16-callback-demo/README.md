# TinyWMS lesson: 16-callback-demo

## Stage purpose
This stage lets an instructor trace one TinyWMS order all the way from the browser and HTTP server to the Lambda order handler, database transaction boundary, queue command, worker, and final pick ticket file. The focus is the full callback chain and the visible JSON at each boundary, not new business features.

## Files in this lesson
- `README.md` - lesson guide for the end-to-end callback path and the local proof.
- `docs/architecture.md` - updated component map showing the assembled chain and the Stage 16 callback proof.
- `docs/data-contracts.md` - contract notes that keep the command, event, and ticket representations visible.
- `docs/end-to-end.md` - instructor walkthrough of the full order path from browser to file output.
- `tests/test_callback_integration.py` - executable local proof of inventory GET, order POST, command emission, worker consumption, and ticket output.
- `tests/test_http_order_flow.py` - inherited HTTP order behavior proof.
- `tests/test_lambda_inventory.py` - inherited Lambda order contract proof.
- `tests/test_pick_ticket_worker.py` - inherited worker/idempotency proof.
- `tests/test_sqs_consumer.py` - inherited queue-consumer proof.
- `tests/test_web_app.js` - inherited browser-contract safety check.
- `src/http_server.py` - local HTTP server reused for the browser/HTTP boundary.
- `src/lambda_inventory.py` - order handler reused for the Lambda/database/SQS/EventBridge boundary.
- `src/pick_ticket_worker.py` - pick-ticket worker reused for the queue-to-file boundary.
- `src/sqs_consumer.py` - queue consumer helper reused by the worker.
- `src/web/index.html` - browser UI for the inventory/order workflow.
- `src/web/app.js` - browser logic that submits the order and refreshes inventory.
- `deploy/pick-ticket-worker/README.md` - worker operations guide for the long-running queue consumer.
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
1. Change the quantity in the temporary order payload used by `tests/test_callback_integration.py`, then run the proof again and observe the changed quantity in the HTTP response and the resulting pick ticket line.
2. Edit the ticket formatting in `src/pick_ticket_worker.py`, observe the changed behavior through the lesson's visible interface, then optionally run the tests.test_callback_integration -v`, and compare the command JSON, worker output, and ticket file contents.
## Continuity note
- Inherited contract: the inventory JSON, order JSON, pick-work command, `OrderPlaced` event, and pick-ticket output contracts remain valid.
- Boundary changed in this stage: the course now emphasizes the full browser-to-worker callback chain and a concrete local proof that exercises the real HTTP server, real order handler, and real worker logic with fake AWS clients at the cloud boundaries.

## Component assembly update
- Added: `tests/test_callback_integration.py` and `docs/end-to-end.md` as the new callback proof and walkthrough artifacts.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/orders.schema.json`, `data/pick-work.json`, `data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/http_server.py`, `src/lambda_inventory.py`, `src/pick_ticket_worker.py`, `src/sqs_consumer.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/pick-ticket-worker/README.md`, `tests/test_http_order_flow.py`, `tests/test_lambda_inventory.py`, `tests/test_pick_ticket_worker.py`, `tests/test_sqs_consumer.py`, and `tests/test_web_app.js`.
- Replaced/evolved: none in this stage; the lesson assembles earlier components into a single visible path and adds a proof that uses them together.

## Cleanup
No external resources are created in this stage. If you start the local HTTP server or worker manually, stop those processes when you are done.
