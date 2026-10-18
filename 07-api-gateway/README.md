# TinyWMS lesson: 07-api-gateway

## Stage purpose
This stage puts API Gateway in front of the Lambda inventory path so students can compare a direct Lambda invoke with a real HTTP front door. The earlier Raspberry Pi/EC2 HTTP server and the browser inventory page stay in the course so the same inventory JSON contract remains visible across both paths.

## Files in this lesson
- `data/inventory.json` - reused sample inventory data that still defines the inventory contract.
- `data/inventory.schema.json` - reused schema for the shared inventory JSON shape.
- `deploy/ec2/README.md` - reused EC2 deployment guide for the direct HTTP server path.
- `deploy/ec2/environment.example` - reused EC2 environment sample.
- `deploy/ec2/run_inventory_server.sh` - reused EC2 startup wrapper.
- `deploy/api-gateway/README.md` - API Gateway deploy, output-resolution, verify, and destroy guide for this stage.
- `docs/architecture.md` - updated component map showing API Gateway as the Lambda front door.
- `docs/data-contracts.md` - updated contract notes for the HTTP and Lambda inventory boundaries.
- `infra/api-gateway.yaml` - CloudFormation template for the API Gateway lesson resources.
- `infra/lambda.yaml` - reused Lambda inventory template that the API Gateway routes to.
- `src/http_server.py` - reused direct HTTP server for the Pi/EC2 path.
- `src/inventory_cli.py` - reused CLI for listing and finding inventory.
- `src/inventory_watcher.py` - reused long-running file/process watcher.
- `src/linux_visible.py` - reused Linux visibility helper.
- `src/lambda_inventory.py` - reused Lambda inventory handler from the prior stage.
- `src/web/app.js` - reused browser client that still fetches the same inventory contract.
- `src/web/index.html` - reused browser page.
- `src/web/style.css` - reused browser styling.
- `tests/test_http_server.py` - reused HTTP contract tests.
- `tests/test_inventory_cli.py` - reused CLI contract tests.
- `tests/test_inventory_watcher.py` - reused watcher tests.
- `tests/test_linux_visible.py` - reused Linux visibility tests.
- `tests/test_lambda_inventory.py` - reused Lambda inventory tests.
- `tests/test_web_app.js` - new Node safety check for the browser contract.

## Run the lesson
From this folder:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Open the browser inventory page, change the API base override to point at either the direct Pi/EC2 server or the API Gateway URL, and observe that the same inventory table renders from both paths.
2. Use `curl` against the direct HTTP server and against API Gateway, then compare the JSON responses to `data/inventory.json`.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible tools, direct HTTP `/inventory` response, browser inventory page, EC2 deployment wrapper, and Lambda inventory handler remain valid and unchanged.
- Boundary changed in this stage: API Gateway becomes the HTTP front door for the Lambda path, while the earlier Pi/EC2 direct HTTP path stays available for comparison.

## Component assembly update
- Added: `infra/api-gateway.yaml` and `deploy/api-gateway/README.md` as the API Gateway front-door component for the Lambda inventory path, plus `tests/test_web_app.js` as a browser-contract safety check.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/lambda_inventory.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, and `tests/test_lambda_inventory.py`.
- Replaced/evolved: `docs/architecture.md` and `docs/data-contracts.md` now document API Gateway as the visible HTTP front door for the Lambda path without changing the inventory JSON contract.

## Cleanup
No external resources are created by the local tests. If you deploy API Gateway or Lambda, destroy the CloudFormation stacks when you are finished and remove any temporary shell variables used to resolve outputs.
