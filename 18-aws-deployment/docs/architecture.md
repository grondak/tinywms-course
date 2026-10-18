# TinyWMS Architecture

## Current architecture

TinyWMS now has twelve visible teaching boundaries: the Stage 1 inventory JSON contract and CLI, the Stage 2 Linux-visible demo tools, the Stage 3 HTTP server that exposes the same inventory JSON over HTTP, the Stage 4 browser page that fetches that same JSON contract, the Stage 5 EC2 deployment wrapper that starts the same HTTP server on a different Linux host, the Stage 6 Lambda inventory handler that returns the same inventory JSON from AWS Lambda, the Stage 7 API Gateway front door that routes HTTP to Lambda, the Stage 8 relational persistence lesson that maps the same inventory model into SQL, the Stage 9 RDS lesson that moves the PostgreSQL database hosting boundary into AWS, Stage 10’s Lambda-to-RDS evolution that changes Lambda’s inventory source from static JSON to database rows without changing the outward inventory JSON contract, Stage 11’s order path that adds transactional inventory decrements and order rows without changing the earlier inventory contract, Stage 12’s concurrency hardening that prevents overselling, Stage 13’s SQS command boundary that publishes pick-work only after the transaction commits, and Stage 14’s EventBridge fact-event boundary that publishes `OrderPlaced` after commit without replacing the command path. The inventory JSON contract remains the canonical data shape; later consumers and deployment steps reuse it rather than replacing it.

SQLite cannot demonstrate the PostgreSQL row-lock lesson.

## Architecture History

- Stage 0: repository scaffold only.
- Stage 1: inventory JSON contract and CLI backbone added.
- Stage 2: Linux-visible demo tools added to make shell, file, and process behavior observable.
- Stage 3: HTTP inventory server added to expose the existing inventory JSON contract over a visible request/response boundary.
- Stage 4: browser inventory page added as another consumer of the same inventory JSON contract.
- Stage 5: EC2 deployment wrapper added as an operations boundary around the same HTTP server and browser assets.
- Stage 6: Lambda inventory handler added as an additional compute boundary for the same inventory JSON contract.
- Stage 7: API Gateway added as the HTTP front door for the Lambda path.
- Stage 8: relational inventory schema, adapter, and initializer added as a SQL representation of the inventory contract.
- Stage 9: RDS added as the managed PostgreSQL hosting and operations boundary for the relational lesson.
- Stage 10: Lambda now reads inventory from the relational database instead of static JSON in the deployed path.
- Stage 11: orders, order lines, and the integrated inventory-and-order browser/local HTTP path were added.
- Stage 12: the existing order transaction was hardened so overlapping requests do not oversell stock.
- Stage 13: committed orders now publish pick-work commands to SQS, and a small consumer helper can receive and acknowledge those commands.
- Stage 14: committed orders also publish an `OrderPlaced` event to EventBridge, and two decoupled consumers read from independent queues.

## Component Assembly Map

| component name | stage introduced | runtime location | inbound contract | outbound contract | dependencies |
| --- | --- | --- | --- | --- | --- |
| inventory JSON file | 01-json-backbone | filesystem (`data/inventory.json`) | none | inventory JSON | none |
| inventory CLI | 01-json-backbone | Linux Python process (`src/inventory_cli.py`) | inventory JSON | printed list output, JSON dump, exit code | inventory JSON file |
| Linux-visible helper | 02-linux-visible | Linux Python process (`src/linux_visible.py`) | stdin, argv, environment variables | stdout, stderr, exit code | standard library, shell-provided stdin/stdout/stderr |
| inventory watcher | 02-linux-visible | Linux Python process (`src/inventory_watcher.py`) | inventory JSON file path, log-file path | repeated JSON snapshots in log file, visible long-running process | inventory JSON file, filesystem append access |
| HTTP inventory server | 03-pi-http-server | Linux Python process (`src/http_server.py`) on Raspberry Pi Linux or EC2 Linux | HTTP `GET /inventory`, environment variable for port, inventory JSON file path | HTTP response with status, headers, and inventory JSON body | inventory JSON file, Python standard library HTTP server |
| browser inventory page | 04-browser | browser (`src/web/index.html`, `src/web/app.js`, `src/web/style.css`) | HTTP `GET /inventory`, browser DOM, optional runtime API base override | rendered HTML table and visible error text | HTTP inventory server, inventory JSON contract, browser `fetch()` |
| EC2 deployment wrapper | 05-ec2-deployment | EC2 Linux host (`deploy/ec2/README.md`, `deploy/ec2/run_inventory_server.sh`) | SSH session, shell environment variables, repository checkout | running HTTP server process on the chosen port | HTTP inventory server, inventory JSON file, EC2 Linux shell |
| Lambda inventory handler | 06-lambda | AWS Lambda (`src/lambda_inventory.py`) | Lambda event input for inventory requests | Lambda response carrying inventory JSON | inventory JSON file, Python standard library JSON and environment handling |
| API Gateway front door | 07-api-gateway | AWS API Gateway (`infra/api-gateway.yaml`, `deploy/api-gateway/README.md`) | HTTP `GET /inventory` from clients | HTTP proxy request into Lambda and HTTP response back to the caller | Lambda inventory handler, Lambda invoke permission |
| relational inventory schema | 08-relational-persistence | SQL files and database process (`data/schema.sql`, `data/seed.sql`, `data/init_db.py`, `src/db_adapter.py`, `src/sql_export.py`) | inventory JSON file and `TINYWMS_DB` / `TINYWMS_SQLITE_PATH` environment variables | `inventory` table rows seeded from the JSON sample | inventory JSON file, SQLite or PostgreSQL backend, lazy PostgreSQL driver import |
| RDS deployment wrapper | 09-rds | AWS RDS / CloudFormation (`infra/rds.yaml`, `deploy/rds/README.md`) | CloudFormation parameters for DB name, credentials, subnet IDs, and security groups | RDS endpoint address and port outputs | relational inventory schema, AWS RDS, CloudFormation |
| Lambda database-backed inventory handler | 10-lambda-rds | AWS Lambda (`src/lambda_inventory.py`) | Lambda event input for inventory requests, PostgreSQL connection settings from environment | Lambda response carrying inventory JSON mapped from database rows | Lambda inventory handler, relational schema, RDS deployment wrapper, database adapter |
| local HTTP inventory/order server | 11-orders | Linux Python process (`src/http_server.py`) | HTTP `GET /inventory` and `POST /orders`, JSON request body, inventory JSON file path | HTTP responses with inventory JSON and order acceptance/rejection JSON | inventory JSON file, order JSON contract, filesystem-backed inventory state |
| integrated inventory and order browser page | 11-orders | browser (`src/web/index.html`, `src/web/app.js`, `src/web/style.css`) | `GET /inventory`, `POST /orders`, same-origin or runtime API base override | refreshed inventory table plus visible request/response JSON | HTTP inventory/order server, inventory JSON contract, order JSON contract |
| Lambda order handler | 11-orders | AWS Lambda (`src/lambda_inventory.py`) | Lambda event input for inventory and order requests | inventory JSON, accepted/rejected order JSON, relational writes | lambda inventory handler, relational schema, order JSON contract |
| concurrent order hardening | 12-concurrency | database transaction boundary (`src/lambda_inventory.py`) | overlapping `place_order(...)` calls against the same inventory row | one accepted order and one clean failure without negative inventory | order handler, relational schema, transaction boundary, PostgreSQL row locking or atomic conditional decrement |
| pick-work command publisher | 13-sqs | AWS Lambda (`src/lambda_inventory.py`) after commit | committed order request plus locked inventory row data | versioned pick-work command JSON sent to SQS | order handler, relational schema, SQS client, queue URL |
| pick-work SQS queue | 13-sqs | AWS SQS (`infra/sqs.yaml`, `deploy/sqs/README.md`) | pick-work command JSON | durable queue message ready for a consumer | order handler, SQS service, CloudFormation deployment |
| SQS consumer helper | 13-sqs | Linux Python process (`src/sqs_consumer.py`) | queue URL and callback function | decoded command JSON delivered to the callback, message delete on success | SQS client, pick-work command contract |
| OrderPlaced event publisher | 14-domain-events | AWS Lambda (`src/lambda_inventory.py`) after commit | committed order request plus `EVENT_BUS_NAME` | versioned `OrderPlaced` event JSON sent to EventBridge | order handler, relational schema, EventBridge client, bus name |
| EventBridge order bus | 14-domain-events | AWS EventBridge (`infra/events.yaml`, `deploy/events/README.md`) | `OrderPlaced` event pattern | fan-out delivery to two target queues | order handler, EventBridge rules, SQS targets, queue policies |
| event consumer A | 14-domain-events | Linux Python process (`src/event_consumer_a.py`) | queue URL for target A and callback semantics | decoded event JSON printed/processed by the consumer | SQS client, event contract |
| event consumer B | 14-domain-events | Linux Python process (`src/event_consumer_b.py`) | queue URL for target B and callback semantics | decoded event JSON printed/processed by the consumer | SQS client, event contract |
| local mode (SQLite, a file queue and a file event bus) | 18-aws-deployment | Python process on Linux (`TINYWMS_LOCAL=1`, `src/local_aws.py`, `deploy/local/run_local.sh`) | the same handler calls and queue/event calls the AWS clients receive | one JSON file per message, with each event copied to both event-consumer queues | Lambda handler, SQLite database |

## Component evolution timeline

- Stage 1 introduced the inventory JSON file and inventory CLI.
- Stage 2 reused the inventory contract and added Linux-visible process/file demos.
- Stage 3 reused the same inventory data and added the HTTP inventory server.
- Stage 4 reused the HTTP server contract and added the browser inventory page.
- Stage 5 reused the HTTP inventory server and added EC2 deployment instructions.
- Stage 6 reused the inventory contract and added the Lambda inventory handler.
- Stage 7 reused the Lambda inventory handler and added API Gateway as the HTTP front door.
- Stage 8 reuses the inventory JSON contract and adds SQL schema, seed, adapter, and initializer components.
- Stage 9 reuses the relational persistence components and adds the managed RDS hosting boundary.
- Stage 10 reuses the Lambda component and changes only its data-source dependency, which now points at the relational/RDS path.
- Stage 11 reuses the inventory and relational contracts and adds orders, order lines, and integrated browser/local HTTP order submission.
- Stage 12 reuses the order handler and makes the transaction boundary concurrency-safe.
- Stage 13 reuses the order handler and adds the SQS publish/consume boundary.
- Stage 14 reuses the order handler and adds the EventBridge fact-event boundary without replacing the queue command boundary.

## Data contract mapping

The inventory JSON object fields map directly to the relational inventory table:

- `sku` -> `inventory.sku`
- `description` -> `inventory.description`
- `bin_location` -> `inventory.bin_location`
- `quantity` -> `inventory.quantity`
- `unit` -> `inventory.unit`

The SQL schema keeps `bin_location` as the canonical column name so the lesson can compare the JSON key and SQL column directly. The seed script is derived from `data/inventory.json` and keeps the same sample rows visible to students.

The order JSON object fields map to the relational order tables:

- `order_id` -> `orders.order_id`
- `status` -> `orders.status`
- `lines[].sku` -> `order_lines.sku`
- `lines[].quantity` -> `order_lines.quantity`

The pick-work command JSON fields map to the queue message shape:

- `command_id` - stable, versioned queue command identifier derived from the order, SKU, quantity, and bin.
- `order_id` - order that triggered the command.
- `sku` - SKU to pick.
- `description` - description copied from the locked inventory row.
- `quantity` - quantity to pick.
- `bin` - bin location copied from the locked inventory row.

The `OrderPlaced` event JSON fields map to the event shape:

- `version` - event schema version.
- `order_id` - order that was placed.
- `lines[]` - the ordered SKU and quantity facts.

The event is intentionally distinct from the command: the command says what to do, while the event says what happened.

## Notes on the current stage

- The SQLite branch exists only as a local teaching path and does not represent a database server process with a network port.
- The PostgreSQL branch remains the default so later lessons can demonstrate a real database service, row locking, and operational deployment.
- SQS changes the post-commit workflow, not the order JSON contract.
- The consumer helper performs one receive/delete cycle per call so Stage 15 can own the long-running process loop.
- EventBridge adds a separate facts channel without removing the queue-based work channel.
- Students can compare self-managed Linux queue/event consumers with AWS-managed delivery without changing the order contract.
- SQLite cannot demonstrate the PostgreSQL row-lock lesson.
