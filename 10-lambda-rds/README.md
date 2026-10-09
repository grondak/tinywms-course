# TinyWMS lesson: 10-lambda-rds

## Stage purpose
This stage changes only one boundary: Lambda now reads inventory from RDS instead of from embedded JSON. The browser and HTTP response contract stay the same, so students can see that the data source changed while the JSON shape did not.

## Files in this lesson
- `src/lambda_inventory.py` - Lambda handler that reads inventory rows from RDS and converts them back into the established inventory JSON contract
- `src/rds_inventory.py` - small database helper for connecting to PostgreSQL and mapping rows into JSON-ready inventory items
- `deploy/lambda-rds/template.json` - teaching deployment template showing the Lambda-to-RDS wiring and required environment variables
- `deploy/lambda-rds/invoke.sh` - local invocation example that simulates Lambda input while using the same handler
- `deploy/rds/bootstrap.sql` - unchanged schema/bootstrap SQL from the previous stage, still the source of truth for the relational tables
- `docs/architecture.md` - updated boundary comparison for static JSON vs Lambda-to-RDS
- `docs/data-contracts.md` - notes that the inventory JSON contract still does not change even though the data source does
- `tests/test_lambda_inventory.py` - checks the Lambda response contract and the RDS mapping helper behavior
- `tests/test_rds_inventory.py` - exercises the row-to-JSON conversion without needing AWS

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
TINYWMS_DB_HOST=127.0.0.1 TINYWMS_DB_PORT=5432 TINYWMS_DB_NAME=tinywms TINYWMS_DB_USER=tinywms TINYWMS_DB_PASSWORD=secret python3 src/lambda_inventory.py < src/lambda_event_example.json
```
The second command shows the Lambda shape locally. It will only succeed if a PostgreSQL-compatible database is reachable with the expected tables and sample rows.

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change `src/rds_inventory.py` so the inventory list is ordered by bin instead of by SKU, then re-run the tests and explain why the JSON contract did not change.
2. Edit `deploy/lambda-rds/template.json` to use a different database port environment variable name, then update the handler and tests to match.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same JSON document with the same `inventory[]` fields used by the browser and previous Lambda stage
- Boundary changed in this stage: Lambda no longer reads embedded JSON; it connects to RDS, reads rows, and maps them back into the existing JSON shape

## Cleanup
No AWS resources are created by the tests. If you deploy the Lambda/RDS wiring, delete the Lambda function, API resources if any, the RDS instance, subnet group, security groups, and any logs or stacks you created to avoid charges.
