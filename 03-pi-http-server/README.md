# TinyWMS lesson: 03-pi-http-server

## Stage purpose
This stage adds the smallest transparent HTTP server so students can see a real request/response boundary around the existing inventory JSON. The same inventory contract from earlier stages is still the source of truth; the new lesson is about how a Linux process listens on a port and returns JSON over HTTP.

## Files in this lesson
- `data/inventory.json` - reused Stage 1 inventory data served by the HTTP endpoint.
- `data/inventory.schema.json` - reused schema that still describes the inventory JSON contract.
- `docs/architecture.md` - updated Component Assembly Map showing the new HTTP server component and the earlier Linux/JSON components it reuses.
- `docs/data-contracts.md` - reused inventory contract notes.
- `src/http_server.py` - new minimal HTTP server for `GET /inventory`.
- `src/inventory_cli.py` - reused CLI for comparing the file-backed inventory contract with the HTTP response.
- `src/linux_visible.py` - reused Linux visibility helper for process and environment exercises.
- `src/inventory_watcher.py` - reused long-running watcher for `tail -f` practice.
- `tests/test_http_server.py` - new tests for the HTTP endpoint and visible response behavior.
- `tests/test_inventory_cli.py` - reused CLI tests from earlier stages.
- `tests/test_linux_visible.py` - reused Linux-visible helper tests from Stage 2.
- `tests/test_inventory_watcher.py` - reused watcher tests from Stage 2.

## Run the lesson
From this folder:
```bash
python3 src/http_server.py
TINYWMS_PORT=8080 python3 src/http_server.py
curl -i http://127.0.0.1:8000/inventory
curl -i http://127.0.0.1:8080/inventory
python3 src/inventory_cli.py data/inventory.json list
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Student exercises
1. Change `TINYWMS_PORT` and start `python3 src/http_server.py`, then use `curl -i` to observe the listening port and the HTTP status, headers, and JSON body.
2. Edit one item in `data/inventory.json`, restart the server, and compare the output of `curl http://127.0.0.1:8000/inventory` with `python3 src/inventory_cli.py data/inventory.json list`.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, and Linux-visible helper scripts from earlier stages remain valid and unchanged.
- Boundary changed in this stage: TinyWMS now exposes the inventory JSON over HTTP with an explicit listening port, request path, response status, headers, and body.

## Component assembly update
- Added: `src/http_server.py` and `tests/test_http_server.py`.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/inventory_cli.py`, `src/linux_visible.py`, `src/inventory_watcher.py`, and their earlier tests are carried forward as the same teaching contracts.
- Replaced/evolved: `README.md` and `docs/architecture.md` are expanded to teach the HTTP boundary and to show how the server depends on the existing inventory JSON contract.

## Cleanup
If you started the HTTP server, stop it with `Ctrl+C`. No external resources are created in this stage.
