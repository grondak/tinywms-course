# TinyWMS lesson: 16-callback-demo

## Stage purpose
This stage prepares an instructor demo of the full asynchronous TinyWMS callback path. Students can place an order from the browser, watch the HTTP request and JSON response, inspect the Lambda/API event shape, see the JSON command and event documents, and finally observe the Linux worker append a human-readable pick ticket to `pick-tickets.txt` with `tail -f`.

## Files in this lesson
- `docs/demo-runbook.md` - step-by-step instructor demo script tracing each boundary and naming the JSON passed at each hop
- `src/demo_trace.py` - prints the visible JSON artifacts used along the end-to-end path so students can compare request, command, event, and file output representations
- `deploy/demo/run-callback-demo.sh` - helper wrapper that runs the local trace script for a quick continuity demo
- `docs/architecture.md` - updated to describe the callback-style demonstration from browser action to Linux file append
- `docs/data-contracts.md` - updated with a boundary-by-boundary summary of the JSON documents visible in the callback demo
- `tests/test_demo_trace.py` - tests the demo trace helper so the stage keeps runnable verified artifacts

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
python3 src/demo_trace.py --order-file data/order-example.json
./deploy/demo/run-callback-demo.sh
```

For the full instructor callback demo, open two terminals.

Terminal 1: watch the Linux file callback:
```bash
rm -f pick-tickets.txt
: > pick-tickets.txt
tail -f pick-tickets.txt
```

Terminal 2: run the worker locally once with the known example message, then inspect the trace artifacts:
```bash
python3 src/demo_trace.py --order-file data/order-example.json
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
cat pick-tickets.txt
```

If you have the cloud pieces deployed already, use the detailed runbook in `docs/demo-runbook.md` to drive the full browser → API Gateway → Lambda → RDS → SQS/EventBridge → worker path.

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `data/order-example.json` to request a different SKU and re-run `python3 src/demo_trace.py --order-file data/order-example.json` to see how the downstream pick-work and event JSON change.
2. Add one more visible field to the trace output in `src/demo_trace.py` such as the expected `/orders` URL, then extend `tests/test_demo_trace.py` and re-run the test suite.

## Continuity note
- Inherited contract: `GET /inventory`, `POST /orders`, the SQS `PickWorkRequested` command, the EventBridge `OrderPlaced` event, and the worker-generated `pick-tickets.txt` artifact all remain valid
- Boundary changed in this stage: no core contract changed; this stage adds instructor-facing demo artifacts that make the complete callback path and its JSON boundaries easier to observe live

## Cleanup
Local demo commands create or append `pick-tickets.txt`, which you can remove with:
```bash
rm -f pick-tickets.txt
```
If you use already-deployed AWS resources for the full cloud walkthrough, clean them up with the same CloudFormation delete commands from the earlier SQS, EventBridge, Lambda/API Gateway, and RDS lessons after class.
