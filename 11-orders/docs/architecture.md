# TinyWMS architecture

## Current architecture
- TinyWMS still has a Lambda inventory path that reads from Amazon RDS and returns the established inventory JSON contract.
- This stage adds a second Lambda/API boundary: `POST /orders`.
- The new order path validates JSON, starts a database transaction, creates relational order rows, decrements inventory, and either commits all changes or rolls them all back.
- The earlier Raspberry Pi, EC2, browser, and relational database lessons still matter because students can compare a simple Linux file-based path with a cloud-backed transactional path.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, files, process, and port behavior.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract.
- The student manages the instance, process, and port.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- The browser now also contains a plain HTML order form that builds an order JSON request and sends it to `/orders`.
- Failures should stay visible to students as HTTP status codes and JSON error bodies.

### Lambda reading and writing RDS
- Lambda now handles both `GET /inventory` and `POST /orders`.
- For `GET /inventory`, Lambda connects to RDS, reads relational rows, and converts them into the established inventory JSON contract.
- For `POST /orders`, Lambda validates the request, inserts into `orders` and `order_lines`, decrements `inventory_locations`, and commits only if all lines can be satisfied.
- AWS is responsible for Lambda execution and RDS hosting, while students still control schema, SQL, credentials, and cost cleanup.

### RDS
- RDS continues to host the same `products` and `inventory_locations` tables.
- This stage adds `orders` and `order_lines` without changing the meaning of the existing inventory tables.
- RDS becomes the source of truth both for inventory reads and for committed order history.

## What stayed the same
- The inventory JSON field names and meanings stayed the same.
- `GET /inventory` remains compatible with the browser and previous tests.
- The relational product and inventory meaning stayed the same.
- The browser inventory table does not need a data-model change.

## What changed in this stage
- TinyWMS gained an order JSON contract and a `POST /orders` HTTP path.
- Lambda now performs database writes as well as reads.
- Transaction boundaries matter visibly: a failed order must not leave partial rows or partial inventory decrements behind.

## Failure and recovery notes
- If Lambda cannot reach RDS, the handler should fail visibly rather than pretending an order succeeded.
- If the order JSON is malformed or incomplete, the request should fail with a clear client error.
- If inventory is insufficient, the request should fail cleanly and the transaction should roll back.
- Students can recover by checking database endpoint, security group, credentials, schema, and seed data, then re-running the order request.

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
