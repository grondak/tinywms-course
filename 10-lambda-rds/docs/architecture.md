# TinyWMS architecture

## Current architecture
- TinyWMS now has a Lambda inventory path that reads from Amazon RDS instead of embedded JSON.
- The established inventory JSON response contract is unchanged.
- The point of this stage is to keep the same browser-facing data model while moving the storage source behind Lambda.
- The earlier Raspberry Pi, EC2, browser, and relational database lessons still matter because they show the same contract at different boundaries.

## Deployment variants
### Raspberry Pi Linux
- The Pi variant still demonstrates a visible Linux process serving JSON directly.
- It remains useful as the simplest place to compare request, response, and file-based inventory data.

### EC2 Linux
- EC2 still runs the same HTTP application with the same `/inventory` response contract.
- The student manages the instance, process, and port.

### Browser client
- The browser still expects the same inventory JSON and renders SKU, description, bin, and quantity.
- No browser model change is required for this stage.

### Lambda reading RDS
- Lambda now receives an event, connects to RDS with environment variables, reads relational rows, and converts them into the established inventory JSON contract.
- The Lambda code now owns the mapping boundary from SQL rows back to JSON.
- AWS is responsible for Lambda execution and RDS hosting, while students still control schema, credentials, and cost cleanup.

### RDS
- The logical schema from `data/schema.sql` and `deploy/rds/bootstrap.sql` is unchanged.
- RDS continues to host the same `products` and `inventory_locations` tables.
- The database is now the shared source of truth for both direct SQL lessons and the Lambda inventory path.

## What stayed the same
- The inventory JSON field names and meanings stayed the same.
- The relational schema stayed the same.
- The JSON-to-table meaning stayed the same.
- The browser does not need a data-model change.

## What changed in this stage
- Lambda stopped returning embedded sample JSON.
- Lambda now depends on database connection settings and a live RDS database.
- The boundary between compute and persistence became more visible because rows must be mapped back into JSON.

## Failure and recovery notes
- If Lambda cannot reach RDS, the handler should fail visibly rather than inventing fake inventory.
- Students can recover by checking the database endpoint, security group, credentials, and seed data.
- Restarting the Lambda is not enough if the database rows are missing; the relational data must be present.

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
