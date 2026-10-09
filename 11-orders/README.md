# TinyWMS lesson: 11-orders

## Stage purpose
This stage introduces a second application contract: warehouse orders. Students can now submit an order as JSON through `POST /orders`, watch Lambda validate it, write relational rows, decrement inventory in one database transaction, and see a clean failure when stock is insufficient.

## Files in this lesson
- `src/lambda_inventory.py` - Lambda handler that now serves both `GET /inventory` and `POST /orders`
- `src/order_service.py` - small order-validation and transaction logic kept separate from the HTTP/Lambda event wrapper
- `src/rds_inventory.py` - database helper extended with order creation and inventory decrement logic
- `src/order_event_example.json` - sample API Gateway style event for a valid order submission
- `src/order_bad_event_example.json` - sample event that requests too much inventory and demonstrates rollback behavior
- `src/web/index.html` - browser page extended with a plain HTML order form next to the inventory view
- `src/web/app.js` - browser JavaScript that still loads inventory and now submits order JSON visibly
- `data/order.schema.json` - JSON Schema document for the minimal order request contract
- `data/order-example.json` - example order document students can inspect and reuse with curl
- `data/schema.sql` - relational schema extended with `orders` and `order_lines`
- `data/seed.sql` - seed data compatible with the extended schema
- `deploy/rds/bootstrap.sql` - RDS bootstrap SQL updated with the new order tables
- `deploy/apigateway/template.json` - API Gateway template extended with `POST /orders`
- `deploy/lambda-rds/template.json` - Lambda deployment template still points to the same handler, now supporting orders too
- `deploy/lambda-rds/invoke-order.sh` - local Lambda-style invocation for a successful order request
- `deploy/lambda-rds/invoke-order-too-many.sh` - local Lambda-style invocation for an insufficient-inventory request
- `docs/architecture.md` - explains the new order boundary and transaction/rollback behavior
- `docs/data-contracts.md` - documents the new order JSON request and response shapes and their table mapping
- `tests/test_lambda_inventory.py` - expanded tests for `POST /orders` success and failure paths
- `tests/test_order_service.py` - focused tests for order validation and response shaping
- `tests/test_rds_inventory.py` - tests for row mapping plus transactional order database logic using SQLite-compatible test connections
- `tests/test_http_server.py` - still proves the old Linux server `GET /inventory` contract remains intact

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
TINYWMS_DB_HOST=127.0.0.1 TINYWMS_DB_PORT=5432 TINYWMS_DB_NAME=tinywms TINYWMS_DB_USER=tinywms TINYWMS_DB_PASSWORD=secret python3 src/lambda_inventory.py < src/lambda_event_example.json
TINYWMS_DB_HOST=127.0.0.1 TINYWMS_DB_PORT=5432 TINYWMS_DB_NAME=tinywms TINYWMS_DB_USER=tinywms TINYWMS_DB_PASSWORD=secret python3 src/lambda_inventory.py < src/order_event_example.json
TINYWMS_PORT=8000 python3 src/http_server.py data/inventory.json
```
The first two commands exercise the Lambda shape locally. The order command requires a PostgreSQL-compatible database loaded with the TinyWMS schema and seed data. The third command runs the older Linux HTTP server path so students can compare the historical `/inventory` implementation with the cloud order path.

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `src/order_service.py` so the order validation rejects duplicate SKUs in one request, then add a test and re-run the suite.
2. Submit `src/order_bad_event_example.json`, inspect the failure JSON, and then query the database to confirm no partial `orders` or `order_lines` rows were committed.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same inventory JSON document used by the browser, CLI examples, and previous Lambda/API Gateway stages
- Boundary changed in this stage: API Gateway and Lambda now also accept `POST /orders`, and Lambda performs a database transaction that writes order rows and decrements inventory in RDS

## Cleanup
No AWS resources are created by the automated tests. If you deploy the Lambda, API Gateway, or RDS resources, delete the Lambda function, API resources, RDS instance, subnet group, security groups, and any logs or stacks you created to avoid charges. If you create test order rows manually, you can reset the lesson state by dropping and recreating the schema with `deploy/rds/bootstrap.sql`.
