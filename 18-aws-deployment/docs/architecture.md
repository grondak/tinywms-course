# TinyWMS architecture

## Current architecture
- TinyWMS still has a Lambda inventory path that reads from Amazon RDS and returns the established inventory JSON contract.
- TinyWMS still accepts `POST /orders` through Lambda and API Gateway.
- The order path still commits inventory and order rows transactionally before reporting success.
- After a successful committed order, TinyWMS still publishes a JSON pick-work command message to Amazon SQS.
- After that same successful committed order, TinyWMS still also publishes a separate `OrderPlaced` domain event to Amazon EventBridge.
- The HTTP request still should not perform pick-ticket generation synchronously. Downstream work still happens later in separate consumers.
- The SQS consumer has already evolved into a long-lived pick-ticket worker that turns queue JSON into a human-readable Linux text file.
- The worker may still run directly on a Raspberry Pi, EC2 Linux, or in a container, and that continuity remains important in this stage.
- This stage adds a reproducible AWS deployment using CloudFormation so the cloud-side architecture can be created, reviewed, updated, and destroyed as a visible set of resources.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.
- In the current architecture, a Raspberry Pi can also still participate as the downstream pick-ticket worker.
- The Pi worker reads the same `PickWorkRequested` JSON from SQS and appends the same human-readable tickets to a local `pick-tickets.txt` file.
- This is important teaching continuity: cloud order placement can still end on a physical Linux machine that students can inspect with `tail -f`.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract in the older deployment path.
- The student still manages the instance, process, and port in that variant.
- EC2 or another Linux machine can also run the long-lived pick-ticket worker process against the SQS queue.
- Students can compare host-managed Linux operation with Lambda-managed execution while keeping the same JSON boundaries visible.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- The browser still contains a plain HTML order form that builds an order JSON request and sends it to `/orders`.
- Failures should stay visible to students as HTTP status codes and JSON error bodies.
- The browser remains the starting point for the callback demo runbook.
- This stage does not change the browser’s data model. It changes how the AWS-side infrastructure is reproducibly created.

### CloudFormation-managed AWS deployment
- This stage introduces a single CloudFormation template that defines the current cloud-side TinyWMS architecture.
- The template creates a small VPC, private subnets, security groups, a PostgreSQL RDS instance, an SQS queue, an EventBridge bus, IAM permissions, the Lambda function, API Gateway routes, and log retention.
- Lambda packaging is intentionally visible through a small Python zip script and an S3 artifact bucket rather than hidden behind a large framework.
- Stack parameters keep account-specific values and secrets out of the repository.
- Stack outputs expose the API base URL, queue URL, event bus name, and database endpoint so students can inspect the exact cloud boundaries.

### Lambda reading and writing RDS
- Lambda still handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, starts a database transaction, inserts into `orders`, attempts conditional inventory decrements, inserts `order_lines`, and commits only if all lines can be satisfied.
- After the commit succeeds, Lambda builds a pick-work JSON command and sends it to SQS.
- After the commit succeeds, Lambda also builds an `OrderPlaced` domain event and sends it to EventBridge.
- In this stage those environment variables and permissions are now reproducibly wired by the CloudFormation stack.

### RDS
- RDS continues to host the same `products`, `inventory_locations`, `orders`, and `order_lines` tables.
- RDS remains the source of truth both for inventory reads and for committed order history.
- This stage does not change the logical relational schema.
- A separate bootstrap step still applies SQL visibly after the database instance exists.
- Students should notice that infrastructure creation and schema creation are separate operational steps.

### SQS command path
- SQS remains the boundary between order placement and later pick processing.
- The queue stores one JSON `PickWorkRequested` command message per committed order.
- That message means a downstream worker is being asked to do a particular task.
- The worker still uses the command plus a product/bin lookup to build a human-readable pick ticket.
- This stage adds reproducible queue creation and Lambda permission to send messages.
- The queue still supports Linux-hosted or Raspberry-Pi-hosted workers outside AWS-managed compute.

### Pick-ticket worker on a Linux host or Raspberry Pi
- The pick-ticket worker is still a small Python Linux process that can run once for a local example or continuously against SQS.
- For each `PickWorkRequested` message, it formats a readable ticket containing order ID, SKU, description, quantity, and bin location.
- It appends each completed ticket to `pick-tickets.txt` instead of printing only raw JSON.
- The worker still logs what it is doing to stdout/stderr so students can inspect it with normal Linux tools.
- In this stage, the worker is intentionally not moved into Lambda. Keeping the Pi/Linux worker path alive preserves the semester’s conceptual history.

### Pick-ticket worker in a container
- The worker container from the previous stage remains valid.
- Students may still run the containerized worker against the deployed SQS queue by supplying `AWS_REGION`, `TINYWMS_SQS_QUEUE_URL`, and a mounted output path.
- Containerization remains a packaging choice for the Linux worker, not a contract change.

### EventBridge event path
- EventBridge is still a second asynchronous boundary after order placement.
- It carries a JSON `OrderPlaced` domain event describing something that already happened.
- The event remains intentionally separate from the SQS command so students can compare imperative and descriptive messaging.
- This stage adds reproducible EventBridge bus creation and visible rules showing where independent consumers could attach.

### Observability
- API Gateway stage metrics and request logging are enabled in the reproducible deployment.
- Lambda logs go to a named CloudWatch log group with an explicit retention period.
- Students should be able to answer where to look when `GET /inventory` or `POST /orders` fails in the cloud path.
- The Linux worker remains observable separately through stdout/stderr and the appended `pick-tickets.txt` file.

## What stayed the same
- The inventory JSON field names and meanings stayed the same.
- `GET /inventory` remains compatible with the browser and previous tests.
- The order request and response JSON shapes stayed the same.
- The relational table meanings stayed the same.
- The existing SQS pick-work command contract stayed available.
- The existing EventBridge `OrderPlaced` contract stayed available.
- The browser inventory table and order form do not need a data-model change.
- The worker still writes the same human-readable pick-ticket text format.
- A Raspberry Pi or Linux host is still a supported deployment target for the pick-ticket worker.

## What changed in this stage
- TinyWMS now includes a reproducible CloudFormation deployment for the current AWS architecture.
- The repository now includes a standard-library Lambda packaging script and deployment helpers.
- API Gateway, Lambda, IAM, RDS connectivity, SQS, EventBridge, and log retention are now visible in one reviewed infrastructure template.
- AWS resource creation and destruction are now documented as repeatable commands rather than only separate teaching fragments.
- Students must now explicitly manage artifact buckets, stack parameters, deploy steps, schema bootstrap, and teardown.

## Failure and recovery notes
- If CloudFormation deployment fails, inspect stack events with the AWS CLI before retrying.
- If Lambda cannot reach RDS, the handler should fail visibly rather than pretending an order succeeded.
- If the database exists but the schema is not bootstrapped, API calls will fail visibly until `bootstrap_rds.sh` is run.
- If the order JSON is malformed or incomplete, the request should fail with a clear client error.
- If inventory is insufficient, the request should fail cleanly and the transaction should roll back.
- If the database commit succeeds but SQS publish fails, the order remains committed in RDS and the publish failure should be visible so students can investigate and replay if needed.
- If the database commit succeeds but EventBridge publish fails, the order remains committed in RDS and the event publish failure should be visible so students can inspect configuration and replay the event if needed.
- If the pick-ticket worker receives a queue message but does not acknowledge it, SQS can retry delivery after the visibility timeout.
- If the Raspberry Pi worker stops, students can restart it and continue consuming later messages because the contract is carried by JSON in SQS rather than hidden in process memory.
- If students forget cleanup, RDS and the artifact bucket can continue incurring cost.

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
- Stage 18: the cloud-side architecture is made reproducibly deployable with CloudFormation, while the Raspberry Pi/Linux worker remains a supported participant in the system.
