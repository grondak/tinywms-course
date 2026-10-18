# TinyWMS lesson: 06-lambda

## Stage purpose
This stage adds an AWS Lambda way to serve the existing TinyWMS inventory contract while keeping the Raspberry Pi and EC2 Linux paths intact. The goal is to compare execution models, not replace the earlier history, so the same inventory JSON shape remains visible at every boundary.

## Files in this lesson
- `data/inventory.json` - reused sample inventory data that Lambda can return unchanged.
- `data/inventory.schema.json` - reused inventory schema for the shared JSON contract.
- `deploy/ec2/README.md` - reused EC2 deployment guide for the earlier HTTP server path.
- `deploy/ec2/environment.example` - reused EC2 environment sample.
- `deploy/ec2/run_inventory_server.sh` - reused EC2 startup wrapper.
- `deploy/lambda/README.md` - Lambda deployment, invoke, verify, and destroy guide for this stage.
- `docs/architecture.md` - updated component map showing Lambda as a parallel compute path.
- `docs/data-contracts.md` - updated contract notes for the Lambda inventory boundary.
- `infra/lambda.yaml` - CloudFormation template for the Lambda lesson resources.
- `src/http_server.py` - reused HTTP server for the Pi/EC2 path.
- `src/inventory_cli.py` - reused CLI for viewing and validating the inventory JSON.
- `src/inventory_watcher.py` - reused long-running file/process watcher.
- `src/linux_visible.py` - reused Linux visibility helper.
- `src/lambda_inventory.py` - new Lambda handler for `GET /inventory`.
- `src/web/app.js` - reused browser client that still fetches the same inventory contract.
- `src/web/index.html` - reused browser page.
- `src/web/style.css` - reused browser styling.
- `tests/test_http_server.py` - reused HTTP contract tests.
- `tests/test_inventory_cli.py` - reused CLI contract tests.
- `tests/test_inventory_watcher.py` - reused watcher tests.
- `tests/test_linux_visible.py` - reused Linux visibility tests.
- `tests/test_web_app.js` - reused browser-contract safety check.
- `tests/test_lambda_inventory.py` - new Lambda behavior tests for the inventory contract.

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
1. Observe the changed behavior through the lesson's visible interface, then optionally run `PYTHONPATH=src python3 -m unittest discover -s tests -v` to confirm the Lambda path still returns the same inventory JSON.
2. Use `deploy/lambda/README.md` to deploy or simulate the Lambda path, then call the function with a payload that triggers `GET /inventory` and compare its JSON output to `data/inventory.json` and the EC2 `/inventory` response.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible helpers, HTTP `/inventory` response, browser inventory page, and EC2 deployment wrapper remain valid and unchanged.
- Boundary changed in this stage: AWS Lambda becomes an additional compute location for the same inventory contract, while the earlier Linux hosting path stays available.

## Component assembly update
- Added: `src/lambda_inventory.py`, `infra/lambda.yaml`, `deploy/lambda/README.md`, and `tests/test_lambda_inventory.py` as the new Lambda inventory component and its teaching safety net.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/http_server.py`, `src/inventory_cli.py`, `src/inventory_watcher.py`, `src/linux_visible.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `deploy/ec2/README.md`, `deploy/ec2/environment.example`, `deploy/ec2/run_inventory_server.sh`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `docs/architecture.md` and `docs/data-contracts.md` now document Lambda as a parallel compute boundary that preserves the same inventory JSON contract.

## Cleanup
No external resources are created by the local tests. If you deploy the Lambda lesson, destroy the CloudFormation stack when you are finished and remove any temporary files or shell variables you created while invoking the function.
