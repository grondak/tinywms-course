# TinyWMS architecture

## Current architecture
- TinyWMS still has the earlier JSON inventory contract used by the CLI, HTTP server, browser, Lambda, and API Gateway stages.
- TinyWMS now adds a relational persistence option for inventory data.
- The relational lesson is intentionally limited to inventory and simple seed data so students can see the mapping from JSON to tables.
- The Lambda/API Gateway path is not changed yet; it still returns the JSON inventory contract without reading from the database.

## Deployment variants
### Raspberry Pi Linux
- Students can still run the HTTP server and browser client on a Pi.
- The Pi remains a useful place to observe ordinary Linux processes and files.

### EC2 Linux
- Students can still run the HTTP server on an EC2 instance.
- EC2 remains a place to observe the same app running on a different Linux host.

### Relational database on ordinary Linux
- Students can run MariaDB or PostgreSQL on a Linux machine and inspect the database process and port directly.
- Students are responsible for starting, stopping, backing up, and cleaning up the database process.
- The database stores rows derived from the TinyWMS JSON inventory contract.

### Lambda and API Gateway
- The Lambda and API Gateway stages still use the inventory JSON file at this point.
- The database is introduced for comparison, not yet as the live backend.

## What stayed the same
- The inventory JSON contract stayed the same.
- The meaning of `sku`, `description`, `bin`, `quantity`, and `unit` stayed the same.
- The browser and HTTP examples still understand the same inventory representation.

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
