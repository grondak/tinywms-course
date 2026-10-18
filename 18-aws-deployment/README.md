# TinyWMS lesson: 18-aws-deployment

## Stage purpose
This stage turns the existing cloud lesson pieces into one deployable AWS stack. Students can now package the real Lambda source, deploy the API, database connectivity, queue, and event resources together, and verify the same inventory and order contracts through one stack output set.

## Files in this lesson
- `deploy/local/run_local.sh` - starts the system on one machine, no AWS needed
- `src/local_aws.py` - configures local mode and provides the directory-backed queue and event bus
- `tests/test_local_stack.py` - drives local mode over HTTP and runs the worker and event consumers
- `README.md` - lesson guide for the consolidated AWS deployment stage.
- `docs/architecture.md` - updated component map for the single-stack cloud view.
- `deploy/aws/README.md` - exact deploy, output-resolution, verify, and destroy commands.
- `infra/template.yaml` - consolidated CloudFormation template for API Gateway, Lambda, RDS wiring, SQS, EventBridge, IAM, and logs.
- `deploy/aws/package_lambda.sh` - packaging helper that builds the deployable Lambda ZIP from `src/lambda_inventory.py` and `src/db_adapter.py`.
- `tests/test_deployment_wiring.py` - standard-library checks for required deploy artifacts, template wiring, forbidden placeholder literals, and command flow.

## Run the whole system on your own machine
No AWS account needed. One command starts the web page, the order API (the same handler code Lambda runs), a SQLite database, a queue, an event bus and the pick-ticket worker:
```bash
bash deploy/local/run_local.sh            # add --reset to start from a clean database
# open http://127.0.0.1:8000/ , submit an order, then in a second terminal:
tail -f pick-tickets.txt
ls local-aws/pick-work local-aws/event-consumer-a      # the queue and the event, as files
export TINYWMS_LOCAL=1
python3 src/event_consumer_a.py local-aws/event-consumer-a
```
How it maps to the cloud design: the SQLite file stands in for RDS, each directory under `local-aws/` is an SQS queue (one JSON file per message), the event bus copies each event into `event-consumer-a` and `event-consumer-b` like the two EventBridge rules in `infra/events.yaml`, and `TINYWMS_LOCAL=1` is the only switch. Real SQS keeps a message hidden while a worker handles it and may deliver it twice; the file queue does neither, so the duplicate and retry lessons still need the tests or the cloud stack.

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
