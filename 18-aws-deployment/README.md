# TinyWMS lesson: 18-aws-deployment

## Stage purpose
This stage turns the existing cloud lesson pieces into one deployable AWS stack. Students can now package the real Lambda source, deploy the API, database connectivity, queue, and event resources together, and verify the same inventory and order contracts through one stack output set.

## Files in this lesson
- `README.md` - lesson guide for the consolidated AWS deployment stage.
- `docs/architecture.md` - updated component map for the single-stack cloud view.
- `deploy/aws/README.md` - exact deploy, output-resolution, verify, and destroy commands.
- `infra/template.yaml` - consolidated CloudFormation template for API Gateway, Lambda, RDS wiring, SQS, EventBridge, IAM, and logs.
- `deploy/aws/package_lambda.sh` - packaging helper that builds the deployable Lambda ZIP from `src/lambda_inventory.py` and `src/db_adapter.py`.
- `tests/test_deployment_wiring.py` - standard-library checks for required deploy artifacts, template wiring, forbidden placeholder literals, and command flow.

## Run the lesson
From the repository root:
```bash
python3 -m unittest discover -s tests -v
```

To build the Lambda package before deployment:
```bash
chmod +x deploy/aws/package_lambda.sh
./deploy/aws/package_lambda.sh tinywms-lambda-bucket tinywms-cloud-inventory
```

To review the consolidated template before deploying:
```bash
sed -n '1,240p' infra/template.yaml
```

## Run tests
```bash
node --test tests/test_web_app.js
```

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Student exercises
1. Change the Lambda environment wiring in `infra/template.yaml`, rebuild the package, and inspect the stack outputs to see how `ApiBaseUrl`, `QueueUrl`, and `EventBusName` are resolved after deployment.
2. Edit the deployment guide to point at a different stack name, redeploy, and then use the resolved API base URL to watch `GET /inventory` and `POST /orders` still work through the same cloud contracts.
## Continuity note
- Inherited contract: the inventory JSON, order JSON, pick-work command, OrderPlaced event, and pick-ticket output contracts remain the same.
- Boundary changed in this stage: the previously separate cloud pieces are now modeled as one deployable AWS stack with explicit packaging, outputs, and verification flow.

## Component assembly update
- Added: `infra/template.yaml`, `deploy/aws/README.md`, `deploy/aws/package_lambda.sh`, and `tests/test_deployment_wiring.py` as the consolidated deployment lesson artifacts.
- Reused unchanged: `src/lambda_inventory.py`, `src/db_adapter.py`, `deploy/api-gateway/README.md`, `deploy/rds/README.md`, `deploy/sqs/README.md`, `deploy/events/README.md`, `deploy/pick-ticket-worker/README.md`, and the existing data contracts.
- Replaced/evolved: the separate cloud deployment paths are now documented as a single AWS stack while preserving the same application contracts and runtime boundaries.

## Cleanup
No external resources are created in this stage by the repository tests themselves. If you deploy the stack, destroy it with the AWS CLI command shown in `deploy/aws/README.md`.
