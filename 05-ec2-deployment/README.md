# TinyWMS lesson: 05-ec2-deployment

## Stage purpose
This stage teaches how the already-working TinyWMS HTTP server can run on Amazon EC2 Linux without changing the app or its JSON behavior. The lesson focuses on SSH, environment variables, process startup, and verifying the same `/inventory` response students already saw on Raspberry Pi Linux.

## Files in this lesson
- `data/inventory.json` - reused sample inventory served by the HTTP server.
- `data/inventory.schema.json` - reused inventory schema for the shared JSON contract.
- `deploy/ec2/README.md` - EC2 operator notes with connect, configure, run, verify, and cleanup commands.
- `deploy/ec2/environment.example` - example environment values needed by the EC2 process.
- `deploy/ec2/run_inventory_server.sh` - wrapper that starts the existing HTTP server from the repository root.
- `docs/architecture.md` - updated Component Assembly Map showing Raspberry Pi and EC2 as deployment variants for the same HTTP app.
- `docs/data-contracts.md` - reused inventory contract documentation.
- `src/http_server.py` - reused HTTP server that serves `/inventory` and the static browser files.
- `src/inventory_cli.py` - reused CLI for comparing file, HTTP, and browser-visible inventory data.
- `src/linux_visible.py` - reused Linux visibility helper.
- `src/inventory_watcher.py` - reused long-running watcher for process and file exercises.
- `src/web/index.html` - reused browser page that still consumes the same inventory JSON.
- `src/web/app.js` - reused browser JavaScript that fetches inventory JSON.
- `src/web/style.css` - reused browser styling.
- `tests/test_http_server.py` - reused HTTP tests that still prove the `/inventory` contract.
- `tests/test_inventory_cli.py` - reused CLI contract tests.
- `tests/test_inventory_watcher.py` - reused watcher tests.
- `tests/test_linux_visible.py` - reused Linux visibility tests.
- `tests/test_web_app.js` - reused Node safety check for the browser JavaScript contract.

## Run the lesson
From this folder:
```bash
ssh ec2-user@YOUR_EC2_PUBLIC_IP
cp deploy/ec2/environment.example deploy/ec2/environment
set -a
. deploy/ec2/environment
set +a
bash deploy/ec2/run_inventory_server.sh
curl -i "http://127.0.0.1:${TINYWMS_PORT:-8000}/inventory"
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `deploy/ec2/environment.example` to change `TINYWMS_PORT`, copy it to `deploy/ec2/environment`, restart the server, and observe the same inventory response on the new port with `curl -i`.
2. Set `TINYWMS_INVENTORY_FILE` to a temporary JSON file with one changed quantity, rerun `bash deploy/ec2/run_inventory_server.sh`, and compare the browser table or `curl` output with the original `data/inventory.json`.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible tools, HTTP `GET /inventory` response, and browser inventory page remain compatible.
- Boundary changed in this stage: hosting responsibility shifts from the Raspberry Pi teaching target to EC2 Linux deployment steps, but the application process and JSON contract stay the same.

## Component assembly update
- Added: `deploy/ec2/README.md`, `deploy/ec2/environment.example`, and `deploy/ec2/run_inventory_server.sh` as the EC2 deployment wrapper for the existing HTTP app.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/http_server.py`, `src/inventory_cli.py`, `src/linux_visible.py`, `src/inventory_watcher.py`, `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, `tests/test_http_server.py`, `tests/test_inventory_cli.py`, `tests/test_inventory_watcher.py`, `tests/test_linux_visible.py`, and `tests/test_web_app.js`.
- Replaced/evolved: `README.md` and `docs/architecture.md` now describe Raspberry Pi and EC2 as alternate deployment locations for the same visible HTTP server.

## Cleanup
If you started the HTTP server on EC2, stop it with `Ctrl+C` or `pkill -f src/http_server.py`. Remove any copied environment file with `rm -f deploy/ec2/environment`. No external cloud resources are created in this stage.
