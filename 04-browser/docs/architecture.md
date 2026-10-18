# TinyWMS Architecture

## Current architecture

TinyWMS now has four visible teaching boundaries: the Stage 1 inventory JSON contract and CLI, the Stage 2 Linux-visible demo tools, the Stage 3 HTTP server that exposes the same inventory JSON over HTTP, and the Stage 4 browser page that fetches that same JSON contract from the server. The inventory JSON contract remains the canonical data shape; later consumers reuse it rather than replacing it.

## Architecture History

- Stage 0: repository scaffold only.
- Stage 1: inventory JSON contract and CLI backbone added.
- Stage 2: Linux-visible demo tools added to make shell, file, and process behavior observable.
- Stage 3: HTTP server added to expose the existing inventory JSON contract over a visible request/response boundary.
- Stage 4: browser inventory page added as another consumer of the same inventory JSON contract.

## Component Assembly Map

| component name | stage introduced | runtime location | inbound contract | outbound contract | dependencies |
| --- | --- | --- | --- | --- | --- |
| inventory JSON file | 01-json-backbone | filesystem (`data/inventory.json`) | none | inventory JSON | none |
| inventory CLI | 01-json-backbone | Linux Python process (`src/inventory_cli.py`) | inventory JSON | printed list output, JSON dump, exit code | inventory JSON file |
| Linux-visible helper | 02-linux-visible | Linux Python process (`src/linux_visible.py`) | stdin, argv, environment variables | stdout, stderr, exit code | standard library, shell-provided stdin/stdout/stderr |
| inventory watcher | 02-linux-visible | Linux Python process (`src/inventory_watcher.py`) | inventory JSON file path, log-file path | repeated JSON snapshots in log file, visible long-running process | inventory JSON file, filesystem append access |
| HTTP inventory server | 03-pi-http-server | Linux Python process (`src/http_server.py`) on Raspberry Pi Linux or EC2 Linux | HTTP `GET /inventory`, environment variable for port, inventory JSON file path | HTTP response with status, headers, and inventory JSON body | inventory JSON file, Python standard library HTTP server |
| browser inventory page | 04-browser | browser (`src/web/index.html`, `src/web/app.js`, `src/web/style.css`) | HTTP `GET /inventory`, browser DOM, optional runtime API base override | rendered HTML table and visible error text | HTTP inventory server, inventory JSON contract, browser `fetch()` |
