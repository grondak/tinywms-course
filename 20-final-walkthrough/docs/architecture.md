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
- The reproducible AWS deployment using CloudFormation remains the current cloud-side deployment path.
- This stage adds a final architecture walkthrough document that traces one order through every current component and compares the cloud path back to earlier Raspberry Pi and Linux concepts.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.
- In the current architecture, a Raspberry Pi can also still participate as the downstream pick-ticket worker.
- The Pi worker reads the same `PickWorkRequested` JSON from SQS and appends the same human-readable tickets to a local `pick-tickets.txt` file.
- This is important teaching continuity: cloud order placement can still end on a physical Linux machine that students can inspect with `tail -f`.
- The final walkthrough in `docs/end-to-end.md` explicitly relates this worker path back to Linux ideas students first saw on the Pi.

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
- This stage does not change the browser’s data model or runtime behavior.

### CloudFormation-managed AWS deployment
- The single CloudFormation template still defines the current cloud-side TinyWMS architecture.
- The template still creates a small VPC, private subnets, security groups, a PostgreSQL RDS instance, an SQS queue, an EventBridge bus, IAM permissions, the Lambda function, API Gateway routes, and log retention.
- Lambda packaging is still intentionally visible through a small Python zip script and an S3 artifact bucket rather than hidden behind a large framework.
- Stack parameters still keep account-specific values and secrets out of the repository.
- Stack outputs still expose the API base URL, queue URL, event bus name, and database endpoint so students can inspect the exact cloud boundaries.

### Lambda reading and writing RDS
- Lambda still handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, starts a database transaction, inserts into `orders`, attempts conditional inventory decrements, inserts `order_lines`, and commits only if all lines can be satisfied.
- After the commit succeeds, Lambda builds a pick-work JSON command and sends it to SQS.
- After the commit succeeds, Lambda also builds an `OrderPlaced` domain event and sends it to EventBridge.
- The final walkthrough documents these steps one by one, including possible failure points and who operates each boundary.

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
- The queue still supports Linux-hosted or Raspberry-Pi-hosted workers outside AWS-managed compute.

### Pick-ticket worker on a Linux host or Raspberry Pi
- The pick-ticket worker is still a small Python Linux process that can run once for a local example or continuously against SQS.
- For each `PickWorkRequested` message, it formats a readable ticket containing order ID, SKU, description, quantity, and bin location.
- It appends each completed ticket to `pick-tickets.txt` instead of printing only raw JSON.
- The worker still logs what it is doing to stdout/stderr so students can inspect it with normal Linux tools.
- In this stage, the worker is intentionally not moved into Lambda. Keeping the Pi/Linux worker path alive preserves the semester’s conceptual history.
- The final walkthrough highlights that the same Linux ideas from early lessons still matter here: process lifetime, environment variables, files, permissions, logs, and signals.

### Pick-ticket worker in a container
- The worker container from the previous stage remains valid.
- Students may still run the containerized worker against the deployed SQS queue by supplying `AWS_REGION`, `TINYWMS_SQS_QUEUE_URL`, and a mounted output path.
- Containerization remains a packaging choice for the Linux worker, not a contract change.

### EventBridge event path
- EventBridge is still a second asynchronous boundary after order placement.
- It carries a JSON `OrderPlaced` domain event describing something that already happened.
- The event remains intentionally separate from the SQS command so students can compare imperative and descriptive messaging.
- Reproducible EventBridge bus creation and visible rules still show where independent consumers could attach.

### Observability
- API Gateway stage metrics and request logging remain enabled in the reproducible deployment.
- Lambda logs still go to a named CloudWatch log group with an explicit retention period.
- Students should be able to answer where to look when `GET /inventory` or `POST /orders` fails in the cloud path.
- The Linux worker remains observable separately through stdout/stderr and the appended `pick-tickets.txt` file.
- The final walkthrough collects these failure and observation points into a single end-to-end trace.

## Final walkthrough view of the architecture
- `docs/end-to-end.md` is now the best single-document guide to the complete final TinyWMS system.
- It follows one order from browser form input to the final appended pick ticket.
- At each hop it names the executing code, compute environment, input JSON, output JSON, network boundary, persistent state, likely failures, and responsible operator or provider.
- It also includes Mermaid diagrams that GitHub can render directly.
- The walkthrough is intentionally not AWS marketing material; it keeps bringing the system back to concrete computing ideas students already know from Linux and Raspberry Pi lessons.

## Git milestone view of the architecture
- This repository now explicitly treats Git history as a teaching tool.
- A student checking out an earlier milestone should see the smaller architecture that existed at that point in the semester.
- The JSON CLI milestone should not already include Lambda, RDS, SQS, EventBridge, Docker, and CloudFormation files pretending they existed from the start.
- The Pi HTTP milestone should show a visible Linux HTTP server before students move on to EC2 and Lambda variants.
- The browser milestone should still consume the same visible inventory JSON contract.
- The database milestones should show the transition from JSON files to relational tables and then from a self-managed Linux database to RDS.
- The queue/event milestones should show asynchronous command and event boundaries appearing after transactional order creation, not before.
- The worker and container milestones should show the Linux process first and the container packaging later.
- The milestone map in `docs/git-milestones.md` is now part of how students navigate the architecture history.

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
- The current runnable code remains unchanged in this stage.

## What changed in this stage
- The repository now includes a final end-to-end walkthrough document for the current architecture.
- Students can review one order path across all current components without stitching the story together from many earlier lessons.
- The architecture documentation now explicitly points students to that walkthrough when they need the complete final-system view.
- This stage does not add a new runtime component or cloud service. It adds a teaching document that integrates the existing ones.

## Failure and recovery notes
- If a student is unsure where a failure happened in the final architecture, start with `docs/end-to-end.md` and identify the last boundary that succeeded.
- If browser requests fail, verify the configured base URL and HTTP response first.
- If API Gateway or Lambda fails, inspect CloudWatch logs and the visible proxy event shape.
- If RDS work fails, check database connectivity, credentials, and schema bootstrap state.
- If the order commits but no ticket appears, inspect SQS queue state, worker stdout/stderr, and file permissions on `pick-tickets.txt`.
- If students want to simplify the system again, use the documented Git milestones to step back to an earlier stage rather than trying to mentally subtract features from the final deployment.
- This stage should not require cloud redeployment because it changes documentation and teaching workflow, not runtime behavior.

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
- Stage 19: documented Git milestones are added so students can check out those earlier architectural moments directly and verify what the system looked like at each step.
- Stage 20: a final end-to-end walkthrough document is added so students can trace one order across the full current system and relate each cloud boundary back to visible Linux and JSON concepts.
