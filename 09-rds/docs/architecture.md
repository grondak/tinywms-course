# TinyWMS Architecture

## Current architecture

TinyWMS now has eight visible teaching boundaries: the Stage 1 inventory JSON contract and CLI, the Stage 2 Linux-visible demo tools, the Stage 3 HTTP server that exposes the same inventory JSON over HTTP, the Stage 4 browser page that fetches that same JSON contract, the Stage 5 EC2 deployment wrapper that starts the same HTTP server on a different Linux host, the Stage 6 Lambda inventory handler that returns the same inventory JSON from AWS Lambda, the Stage 7 API Gateway front door that routes HTTP to Lambda, the Stage 8 relational persistence lesson that maps the same inventory model into SQL, and the Stage 9 RDS lesson that moves the PostgreSQL database hosting boundary into AWS. The inventory JSON contract remains the canonical data shape; later consumers and deployment steps reuse it rather than replacing it.

## Architecture History

- Stage 0: repository scaffold only.
- Stage 1: inventory JSON contract and CLI backbone added.
- Stage 2: Linux-visible demo tools added to make shell, file, and process behavior observable.
- Stage 3: HTTP server added to expose the existing inventory JSON contract over a visible request/response boundary.
- Stage 4: browser inventory page added as another consumer of the same inventory JSON contract.
- Stage 5: EC2 deployment wrapper added as an operations boundary around the same HTTP server and browser assets.
- Stage 6: Lambda inventory handler added as an additional compute boundary for the same inventory JSON contract.
- Stage 7: API Gateway added as the HTTP front door for the Lambda path.
- Stage 8: relational inventory schema, adapter, and initializer added as a SQL representation of the inventory contract.
- Stage 9: RDS added as the managed PostgreSQL hosting and operations boundary for the relational lesson.

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

## Data contract mapping

The inventory JSON object fields map directly to the relational inventory table:

- `sku` -> `inventory.sku`
- `description` -> `inventory.description`
- `bin_location` -> `inventory.bin_location`
- `quantity` -> `inventory.quantity`
- `unit` -> `inventory.unit`

The SQL schema keeps `bin_location` as the canonical column name so the lesson can compare the JSON key and SQL column directly. The seed script is derived from `data/inventory.json` and keeps the same sample rows visible to students.

## Notes on the current stage

- The SQLite branch exists only as a local teaching path and does not represent a database server process with a network port.
- The PostgreSQL branch remains the default so later lessons can demonstrate a real database service, row locking, and operational deployment.
- RDS changes the hosting and operations responsibility, not the logical relational schema.
- Students can compare self-managed Linux database setup with AWS-managed database setup without changing the inventory contract.
