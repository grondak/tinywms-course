# TinyWMS architecture

## Current architecture
- TinyWMS still has a Lambda inventory path that reads from Amazon RDS and returns the established inventory JSON contract.
- TinyWMS still accepts `POST /orders` through Lambda and API Gateway.
- The order path still commits inventory and order rows transactionally before reporting success.
- After a successful committed order, TinyWMS now publishes a JSON pick-work message to Amazon SQS.
- The HTTP request no longer needs to perform pick-ticket generation synchronously. That downstream work can happen later in a separate consumer process.
- The earlier Raspberry Pi, EC2, browser, and relational database lessons still matter because students can compare a simple Linux file-based path with a cloud-backed transactional and queue-based path.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.
- In this stage, a Pi or any Linux host can also run the new Python SQS consumer to poll and print pick-work messages.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract.
- The student manages the instance, process, and port.
- EC2 or another Linux machine can also be used as the long-running queue consumer host.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- The browser still contains a plain HTML order form that builds an order JSON request and sends it to `/orders`.
- Failures should stay visible to students as HTTP status codes and JSON error bodies.
- The browser does not need to know that downstream pick work has become asynchronous.

### Lambda reading and writing RDS
- Lambda still handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, starts a database transaction, inserts into `orders`, attempts conditional inventory decrements, inserts `order_lines`, and commits only if all lines can be satisfied.
- After the commit succeeds, Lambda builds a pick-work JSON document and sends it to SQS.
- If the queue publish fails after commit, the HTTP request should fail visibly rather than pretending the asynchronous handoff succeeded.
- AWS is responsible for Lambda execution, SQS availability, and RDS hosting, while students still control schema, SQL, queue wiring, credentials, and cost cleanup.

### RDS
- RDS continues to host the same `products`, `inventory_locations`, `orders`, and `order_lines` tables.
- RDS remains the source of truth both for inventory reads and for committed order history.
- This stage does not change the relational schema.

### SQS
- SQS is now the boundary between order placement and later pick processing.
- The queue stores one JSON pick-work command message per committed order.
- Message IDs, receipt handles, acknowledgement, and retry behavior should remain visible in code and command-line output.
- The queue is inexpensive but not free forever, so students should destroy it when finished.

### Queue consumer
- A small Python consumer can poll SQS, print message metadata and body, and optionally delete the message as an explicit acknowledgement.
- If the consumer does not acknowledge a message, SQS can deliver it again after the visibility timeout.
- This visibility helps students understand retries without introducing more infrastructure yet.

## What stayed the same
- The inventory JSON field names and meanings stayed the same.
- `GET /inventory` remains compatible with the browser and previous tests.
- The order request and response JSON shapes stayed the same.
- The relational table meanings stayed the same.
- The browser inventory table and order form do not need a data-model change.

## What changed in this stage
- TinyWMS gained a new asynchronous boundary after successful order commit.
- The system now creates a separate pick-work JSON command message.
- TinyWMS publishes that message to Amazon SQS.
- A separate Python process can receive and acknowledge queue messages.
- Students can now compare synchronous request/response work with delayed queue-based work.

## Failure and recovery notes
- If Lambda cannot reach RDS, the handler should fail visibly rather than pretending an order succeeded.
- If the order JSON is malformed or incomplete, the request should fail with a clear client error.
- If inventory is insufficient, the request should fail cleanly and the transaction should roll back.
- If the database commit succeeds but SQS publish fails, the order remains committed in RDS and the publish failure should be visible so students can investigate and replay if needed.
- If a consumer receives a message but does not delete it, SQS can retry delivery after the visibility timeout.
- Students can recover by checking database settings, queue URL, AWS region, IAM permissions, and queue contents, then re-running the consumer or republishing a known example message.

## Architecture History
- Stage 0: repository scaffold only.
- Stage 1: JSON inventory contract and CLI reader.
- Stage 2: Linux-visible command-line examples.
- Stage 3: Raspberry Pi / EC2-style HTTP server added.
- Stage 4: browser client added.
- Stage 5: EC2 deployment scripts and documentation added without changing the app contract.
- Stage 6: Lambda implementation added alongside the existing Linux server path.
- Stage 7: API Gateway added in front of Lambda without changing the inventory contract.
- Stage 8: relational schema and JSON-to-table mapping added while preserving the existing inventory contract.
- Stage 9: Amazon RDS added as a managed deployment option for the same relational schema.
- Stage 10: Lambda reads inventory from RDS and maps rows back into the unchanged inventory JSON contract.
- Stage 11: Lambda also accepts orders, writes `orders` and `order_lines`, decrements inventory transactionally, and rolls back cleanly on insufficient stock.
- Stage 12: a concurrency demo exposes the naive oversell race, and the order SQL changes to a conditional decrement strategy that preserves the same API contract under concurrent load.
- Stage 13: after a successful committed order, Lambda publishes a JSON pick-work command to SQS and a separate Python consumer can receive, print, retry, and acknowledge that asynchronous work.
