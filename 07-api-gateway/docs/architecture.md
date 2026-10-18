# TinyWMS Architecture

## Current architecture

TinyWMS now has six visible teaching boundaries: the Stage 1 inventory JSON contract and CLI, the Stage 2 Linux-visible demo tools, the Stage 3 HTTP server that exposes the same inventory JSON over HTTP, the Stage 4 browser page that fetches that same JSON contract, the Stage 5 EC2 deployment wrapper that starts the same HTTP server on a different Linux host, and the Stage 6 Lambda inventory handler that returns the same inventory JSON from AWS Lambda. The inventory JSON contract remains the canonical data shape; later consumers and deployment steps reuse it rather than replacing it.

## Architecture History

- Stage 0: repository scaffold only.
- Stage 1: inventory JSON contract and CLI backbone added.
- Stage 2: Linux-visible demo tools added to make shell, file, and process behavior observable.
- Stage 3: HTTP server added to expose the existing inventory JSON contract over a visible request/response boundary.
- Stage 4: browser inventory page added as another consumer of the same inventory JSON contract.
- Stage 5: EC2 deployment wrapper added as an operations boundary around the same HTTP server and browser assets.
- Stage 6: Lambda inventory handler added as an additional compute boundary for the same inventory JSON contract.

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
