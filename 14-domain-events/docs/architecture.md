# TinyWMS architecture

## Current architecture
- TinyWMS still has a Lambda inventory path that reads from Amazon RDS and returns the established inventory JSON contract.
- TinyWMS still accepts `POST /orders` through Lambda and API Gateway.
- The order path still commits inventory and order rows transactionally before reporting success.
- After a successful committed order, TinyWMS still publishes a JSON pick-work command message to Amazon SQS.
- After that same successful committed order, TinyWMS now also publishes a separate `OrderPlaced` domain event to Amazon EventBridge.
- The HTTP request still should not perform pick-ticket generation synchronously. Downstream work can happen later in separate consumers.
- The earlier Raspberry Pi, EC2, browser, and relational database lessons still matter because students can compare a simple Linux file-based path with a cloud-backed transactional, queue-based, and event-driven path.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.
- In this stage, a Pi or any Linux host can also run the Python SQS consumer and the new local event consumer scripts that read JSON from standard input.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract.
- The student manages the instance, process, and port.
- EC2 or another Linux machine can also be used as the long-running queue consumer host or as a host for small event-driven teaching scripts.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- The browser still contains a plain HTML order form that builds an order JSON request and sends it to `/orders`.
- Failures should stay visible to students as HTTP status codes and JSON error bodies.
- The browser does not need to know that downstream systems now receive both a command and a domain event.

### Lambda reading and writing RDS
- Lambda still handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, starts a database transaction, inserts into `orders`, attempts conditional inventory decrements, inserts `order_lines`, and commits only if all lines can be satisfied.
- After the commit succeeds, Lambda builds a pick-work JSON command and sends it to SQS.
- After the commit succeeds, Lambda also builds an `OrderPlaced` domain event and sends it to EventBridge.
- If either asynchronous publish step fails after commit, the failure should be visible rather than hidden.
- AWS is responsible for Lambda execution, EventBridge availability, SQS availability, and RDS hosting, while students still control schema, SQL, queue wiring, event wiring, credentials, and cost cleanup.

### RDS
- RDS continues to host the same `products`, `inventory_locations`, `orders`, and `order_lines` tables.
- RDS remains the source of truth both for inventory reads and for committed order history.
- This stage does not change the relational schema.

### SQS command path
- SQS remains the boundary between order placement and later pick processing.
- The queue stores one JSON `PickWorkRequested` command message per committed order.
- That message means a downstream worker is being asked to do a particular task.
- Message IDs, receipt handles, acknowledgement, and retry behavior should remain visible in code and command-line output.

### EventBridge event path
- EventBridge is now a second asynchronous boundary after order placement.
- It carries a JSON `OrderPlaced` domain event describing something that already happened.
- The event is intentionally separate from the SQS command so students can compare imperative and descriptive messaging.
- EventBridge rules can fan out the same event to more than one independent consumer without changing the order Lambda's business logic.

### Independent event consumers
- One small Python consumer can react to `OrderPlaced` as a shipping-style notification.
- Another small Python consumer can react to the same `OrderPlaced` event as an audit-style log.
- Neither consumer needs to call the order Lambda or know who else is consuming the event.
- This helps students see why events reduce coupling between the producer and later reactions.

## What stayed the same
- The inventory JSON field names and meanings stayed the same.
- `GET /inventory` remains compatible with the browser and previous tests.
- The order request and response JSON shapes stayed the same.
- The relational table meanings stayed the same.
- The existing SQS pick-work command contract stayed available.
- The browser inventory table and order form do not need a data-model change.

## What changed in this stage
- TinyWMS gained a second asynchronous boundary after successful order commit.
- The system now creates a separate `OrderPlaced` domain event.
- TinyWMS publishes that event to Amazon EventBridge.
- At least two independent consumers can react to the same event without being called directly by the order Lambda.
- Students can now compare command-driven queue processing with event-driven fan-out.

## Failure and recovery notes
- If Lambda cannot reach RDS, the handler should fail visibly rather than pretending an order succeeded.
- If the order JSON is malformed or incomplete, the request should fail with a clear client error.
- If inventory is insufficient, the request should fail cleanly and the transaction should roll back.
- If the database commit succeeds but SQS publish fails, the order remains committed in RDS and the publish failure should be visible so students can investigate and replay if needed.
- If the database commit succeeds but EventBridge publish fails, the order remains committed in RDS and the event publish failure should be visible so students can inspect configuration and replay the event if needed.
- If a consumer receives a queue message but does not delete it, SQS can retry delivery after the visibility timeout.
- If an event consumer fails, EventBridge routing and retry behavior should be inspected separately from the order transaction because the event is no longer inside the order Lambda's local control flow.
- Students can recover by checking database settings, queue URL, event bus name, AWS region, IAM permissions, queue contents, and event routing, then re-running consumers or replaying a known example message or event.

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
- Stage 14: after a successful committed order, Lambda also publishes a versioned `OrderPlaced` domain event to EventBridge, and independent consumers can react to that event without being directly coupled to the order handler.
