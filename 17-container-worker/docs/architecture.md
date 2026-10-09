# TinyWMS architecture

## Current architecture
- TinyWMS still has a Lambda inventory path that reads from Amazon RDS and returns the established inventory JSON contract.
- TinyWMS still accepts `POST /orders` through Lambda and API Gateway.
- The order path still commits inventory and order rows transactionally before reporting success.
- After a successful committed order, TinyWMS still publishes a JSON pick-work command message to Amazon SQS.
- After that same successful committed order, TinyWMS still also publishes a separate `OrderPlaced` domain event to Amazon EventBridge.
- The HTTP request still should not perform pick-ticket generation synchronously. Downstream work still happens later in separate consumers.
- The SQS consumer has now evolved into a long-lived pick-ticket worker that turns queue JSON into a human-readable Linux text file.
- This stage keeps that same worker logic but adds a Docker image so students can run the same process in a packaged container environment.
- The earlier Raspberry Pi, EC2, browser, and relational database lessons still matter because students can compare a simple Linux file-based path with a cloud-backed transactional, queue-based, event-driven, and now containerized worker path.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.
- In this stage, a Pi or any Linux host can still run the Python pick-ticket worker as a long-lived process or `systemd` service.
- That worker appends human-readable tickets to a local `pick-tickets.txt` file that students can inspect with `cat`, `tail`, and `tail -f`.
- The callback demo intentionally ends on this local Linux file so students can relate cloud messaging back to familiar Linux tools.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract.
- The student manages the instance, process, and port.
- EC2 or another Linux machine can also run the long-lived pick-ticket worker process against the SQS queue.
- This makes Linux process supervision, service restart behavior, stdout/stderr logs, and local file output visible in a cloud-hosted Linux environment.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- The browser still contains a plain HTML order form that builds an order JSON request and sends it to `/orders`.
- Failures should stay visible to students as HTTP status codes and JSON error bodies.
- The browser remains the starting point for the callback demo runbook.
- The browser does not need to know that downstream systems now receive both a command and a domain event, nor that a Linux worker may now run inside a container before writing pick tickets to a file.

### Lambda reading and writing RDS
- Lambda still handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, starts a database transaction, inserts into `orders`, attempts conditional inventory decrements, inserts `order_lines`, and commits only if all lines can be satisfied.
- After the commit succeeds, Lambda builds a pick-work JSON command and sends it to SQS.
- After the commit succeeds, Lambda also builds an `OrderPlaced` domain event and sends it to EventBridge.
- If either asynchronous publish step fails after commit, the failure should be visible rather than hidden.
- In the callback demo, this is the key teaching boundary where one HTTP JSON request becomes database writes plus two separate asynchronous JSON documents.
- AWS is responsible for Lambda execution, EventBridge availability, SQS availability, and RDS hosting, while students still control schema, SQL, queue wiring, event wiring, credentials, and cost cleanup.

### RDS
- RDS continues to host the same `products`, `inventory_locations`, `orders`, and `order_lines` tables.
- RDS remains the source of truth both for inventory reads and for committed order history.
- This stage does not change the relational schema.
- Students should still be reminded that RDS persistence happens before the worker file is updated.

### SQS command path
- SQS remains the boundary between order placement and later pick processing.
- The queue stores one JSON `PickWorkRequested` command message per committed order.
- That message means a downstream worker is being asked to do a particular task.
- The worker still uses the command plus a product/bin lookup to build a human-readable pick ticket.
- Message IDs, receipt handles, acknowledgement, retries, output file path, and append behavior should remain visible in code and command-line output.
- Containerization does not change the SQS message contract; it only changes how the worker process is packaged and launched.

### Pick-ticket worker on a Linux host
- The pick-ticket worker is still a small Python Linux process that can run once for a local example or continuously against SQS.
- For each `PickWorkRequested` message, it formats a readable ticket containing order ID, SKU, description, quantity, and bin location.
- It appends each completed ticket to `pick-tickets.txt` instead of printing only raw JSON.
- The worker still logs what it is doing to stdout/stderr so students can inspect it with normal Linux tools.
- If the worker receives a bad message or cannot build a ticket, the failure should remain visible and the message should not be silently acknowledged.

### Pick-ticket worker in a container
- This stage adds a Docker image for the same worker process instead of rewriting the worker in a new framework.
- The container still runs one visible Python process: `python3 src/pick_ticket_worker.py`.
- Environment variables such as `TINYWMS_SQS_QUEUE_URL`, `AWS_REGION`, and `TINYWMS_PICK_TICKETS_PATH` remain visible at the container boundary.
- The pick-ticket output file should be stored on a mounted host directory so students can see that container files are ephemeral unless a volume or bind mount is used.
- Students can compare: host process command line, image build, container run command, mounted path, and logs from stdout/stderr.
- This keeps the lesson focused on containers as packaged execution environments for an already-understood Linux process.

### EventBridge event path
- EventBridge is still a second asynchronous boundary after order placement.
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
- The existing EventBridge `OrderPlaced` contract stayed available.
- The browser inventory table and order form do not need a data-model change.
- The worker still writes the same human-readable pick-ticket text format.
- The worker is still the same Python program students already saw in the previous stage.

## What changed in this stage
- TinyWMS now includes a small Dockerfile for the pick-ticket worker only.
- The repository now shows how to build an image and run the same worker process in a container.
- The worker can now read its output path from an environment variable so the container run command can demonstrate configuration at the container boundary.
- The lesson now explicitly demonstrates mounted persistent output so students can compare container filesystem behavior with ordinary Linux files.

## Failure and recovery notes
- If Lambda cannot reach RDS, the handler should fail visibly rather than pretending an order succeeded.
- If the order JSON is malformed or incomplete, the request should fail with a clear client error.
- If inventory is insufficient, the request should fail cleanly and the transaction should roll back.
- If the database commit succeeds but SQS publish fails, the order remains committed in RDS and the publish failure should be visible so students can investigate and replay if needed.
- If the database commit succeeds but EventBridge publish fails, the order remains committed in RDS and the event publish failure should be visible so students can inspect configuration and replay the event if needed.
- If the pick-ticket worker receives a queue message but does not acknowledge it, SQS can retry delivery after the visibility timeout.
- If the worker cannot format or append a ticket, it should log the failure visibly so students can inspect the bad message, output path, or lookup configuration.
- If the worker process stops, students can restart it and continue consuming later messages because the contract is carried by JSON in SQS rather than hidden in process memory.
- If the container exits unexpectedly, students can inspect `docker logs`, verify environment variables, verify the mounted output directory, and rerun the same image with the same command.
- If the container writes no host-visible file, students should check whether `TINYWMS_PICK_TICKETS_PATH` points into the mounted directory and whether the `docker run -v` argument was correct.

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
- Stage 15: the SQS consumer evolves into a long-lived pick-ticket worker that turns `PickWorkRequested` JSON into human-readable warehouse tickets appended to a Linux text file.
- Stage 16: instructor demo artifacts are added so students can trace the complete callback path from browser request to Linux file append and inspect the JSON at each boundary.
- Stage 17: the pick-ticket worker is packaged into a simple Docker image so students can compare the same Linux process running directly on a host versus inside a container.
