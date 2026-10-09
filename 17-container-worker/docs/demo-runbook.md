# TinyWMS callback demo runbook

## Purpose
Use this runbook when you want students to watch one order travel through the whole TinyWMS system and finally appear as a pick ticket in a Linux text file.

The target classroom moment is:
- one terminal running `tail -f pick-tickets.txt`
- one browser submitting an order
- students tracing the intermediate JSON contracts instead of treating the system as a black box

## Demo map
1. Browser builds order request JSON.
2. Browser sends HTTP `POST /orders`.
3. API Gateway wraps the HTTP request as a Lambda proxy event JSON document.
4. Lambda validates the request, writes the RDS transaction, then creates two asynchronous JSON documents:
   - SQS command: `PickWorkRequested`
   - EventBridge event: `OrderPlaced`
5. Python worker reads the SQS command and appends a human-readable ticket to `pick-tickets.txt`.

## Files to have open during the demo
- `src/web/index.html` - browser form fields
- `src/web/app.js` - browser `fetch()` code and visible JSON request body
- `src/lambda_inventory.py` - Lambda entry point for `POST /orders`
- `src/order_service.py` - validation, database write, SQS publish, EventBridge publish
- `src/pick_work.py` - builds the SQS command JSON
- `src/domain_events.py` - builds the EventBridge event JSON
- `src/pick_ticket_worker.py` - Linux worker that writes the file
- `src/pick_ticket.py` - human-readable pick-ticket formatting
- `docs/data-contracts.md` - field-by-field contract meanings

## Terminal setup
Open three terminals if possible.

### Terminal 1: watch the final Linux file
```bash
rm -f pick-tickets.txt
: > pick-tickets.txt
tail -f pick-tickets.txt
```
This terminal should stay visible to the class.

### Terminal 2: show the JSON artifacts used in the path
```bash
python3 src/demo_trace.py --order-file data/order-example.json
```
This prints:
- browser order request JSON
- example Lambda proxy event JSON
- derived SQS command JSON
- derived EventBridge event JSON
- expected pick-ticket text output

### Terminal 3: run or inspect the worker
Local one-shot continuity demo:
```bash
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
```
Long-running worker against a real queue:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export AWS_REGION=us-east-1
python3 src/pick_ticket_worker.py --poll-seconds 2 --output pick-tickets.txt
```

## Local continuity demo
Use this if cloud resources are not deployed today.

1. Print the visible contracts:
```bash
python3 src/demo_trace.py --order-file data/order-example.json
```
2. In another terminal, keep watching the file:
```bash
tail -f pick-tickets.txt
```
3. Append the known example ticket:
```bash
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
```
4. Point out that the final file append is produced from JSON command data, not from hidden in-memory state.

## Full cloud demo
Use this if API Gateway, Lambda, RDS, EventBridge, and SQS are already deployed from earlier lessons.

### 1. Start the worker on a Linux host
On the machine that will write `pick-tickets.txt`:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export AWS_REGION=us-east-1
python3 src/pick_ticket_worker.py --poll-seconds 2 --output pick-tickets.txt
```
Or use the wrapper:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
./deploy/sqs/run-pick-ticket-worker.sh
```

### 2. Watch the final callback landing point
In a second terminal on that same machine:
```bash
rm -f pick-tickets.txt
: > pick-tickets.txt
tail -f pick-tickets.txt
```

### 3. Open the browser UI
If serving the static browser locally:
```bash
python3 src/http_server.py data/inventory.json
```
Then visit:
- `http://localhost:8000/`

If using the browser against API Gateway, set the browser base URL field to something like:
- `https://abc123.execute-api.us-east-1.amazonaws.com/prod`

### 4. Show the browser request JSON before clicking submit
In the page:
- set customer and SKU fields
- point at the `JSON request body` box
- explain that this is the exact JSON contract from `docs/data-contracts.md`

Example request body:
```json
{
  "customer": "Example School Store",
  "lines": [
    {
      "sku": "SKU-1001",
      "quantity": 1
    }
  ]
}
```

### 5. Explain the HTTP boundary
When the browser clicks submit:
- HTTP method: `POST`
- path: `/orders`
- request `Content-Type`: `application/json`
- response: JSON success or JSON error

### 6. Show the API Gateway to Lambda event shape
You can show the example event shape with:
```bash
cat src/order_event_example.json
```
Point out:
- `httpMethod`
- `path`
- `headers`
- `body`

Explain that the original order JSON now lives inside the `body` string of the Lambda proxy event.

### 7. Explain the RDS transaction boundary
Use `src/order_service.py` and `src/rds_inventory.py` to point at:
- request validation
- `orders` insert
- conditional inventory decrement
- `order_lines` insert
- commit

Important teaching note:
- the order is committed in RDS before the worker updates `pick-tickets.txt`
- the file update is asynchronous downstream work

### 8. Show the SQS command JSON
Print the known example command:
```bash
cat data/pick-work-message-example.json
```
Or derive one from the sample order:
```bash
python3 src/demo_trace.py --order-file data/order-example.json
```
Point out that `PickWorkRequested` is a command telling a downstream worker what to do.

### 9. Show the EventBridge event JSON
Print the known example event:
```bash
cat data/order-placed-event-example.json
```
Or derive one from the sample order:
```bash
python3 src/demo_trace.py --order-file data/order-example.json
```
Point out that `OrderPlaced` is an event describing something that already happened.

### 10. Submit the order from the browser
After clicking submit, keep the class watching:
- browser order response JSON
- worker stdout logs
- `tail -f pick-tickets.txt`

The observable end state should be a new appended ticket in Terminal 1.

## Verification checklist
Use these checks during or after the demo.

### Browser / HTTP
- The browser shows a JSON request body before submission.
- The browser receives `HTTP 201` for a successful order.

### Lambda / RDS
- Inventory decreases after the order.
- If inventory is insufficient, the browser shows a visible JSON error.

### SQS / worker
- Worker logs `received messageId=...`.
- Worker logs `wrote pick ticket orderId=...`.
- If ack is enabled, worker logs `acknowledged messageId=...`.

### Linux file callback
- `tail -f pick-tickets.txt` shows the appended human-readable ticket.
- `cat pick-tickets.txt` shows order ID, customer, SKU, quantity, and bin.

## Boundary-by-boundary JSON summary
### Browser request JSON
```json
{
  "customer": "Example School Store",
  "lines": [
    { "sku": "SKU-1001", "quantity": 1 }
  ]
}
```

### Lambda proxy event JSON wrapper
```json
{
  "httpMethod": "POST",
  "path": "/orders",
  "headers": {
    "content-type": "application/json",
    "accept": "application/json"
  },
  "body": "{\n  \"customer\": \"Example School Store\",\n  \"lines\": [\n    {\n      \"sku\": \"SKU-1001\",\n      \"quantity\": 1\n    }\n  ]\n}",
  "isBase64Encoded": false
}
```

### SQS command JSON
```json
{
  "messageType": "PickWorkRequested",
  "version": 1,
  "orderId": 42,
  "customer": "Example School Store",
  "createdAt": "2026-01-15T10:30:00Z",
  "lines": [
    { "lineNumber": 1, "sku": "SKU-1001", "quantity": 1 }
  ]
}
```

### EventBridge event JSON
```json
{
  "eventType": "OrderPlaced",
  "version": 1,
  "orderId": 42,
  "customer": "Example School Store",
  "placedAt": "2026-01-15T10:30:00Z",
  "lines": [
    { "lineNumber": 1, "sku": "SKU-1001", "quantity": 1 }
  ]
}
```

## Recovery notes
- If the browser fails, verify the base URL.
- If API Gateway fails, inspect the Lambda route and deployment stage.
- If Lambda fails, inspect environment variables for database and queue configuration.
- If RDS fails, verify connectivity and credentials.
- If the order commits but no ticket appears, check SQS queue URL, worker logs, and file permissions.
- If needed, replay the known sample message with:
```bash
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
```

## Cleanup
Local demo cleanup:
```bash
rm -f pick-tickets.txt
```
If you ran the live cloud demo, stop the worker with `Ctrl+C` and destroy AWS resources later using the delete commands documented in the earlier deployment lessons.
