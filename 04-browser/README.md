# TinyWMS lesson: 04-browser

## Stage purpose
This stage adds a deliberately simple browser page that uses plain JavaScript `fetch()` to read the same inventory JSON contract already used by the CLI and HTTP server. The lesson is about the browser as another visible consumer of an existing contract, not about frontend frameworks.

## Files in this lesson
- `data/inventory.json` - reused sample inventory served by the HTTP server and rendered in the browser.
- `data/inventory.schema.json` - reused inventory schema that still defines the shared JSON shape.
- `docs/architecture.md` - updated Component Assembly Map showing the browser as a new consumer of `GET /inventory`.
- `docs/data-contracts.md` - reused inventory contract documentation.
- `src/http_server.py` - reused HTTP server that serves `/inventory` and the static browser files.
- `src/inventory_cli.py` - reused CLI for comparing file, HTTP, and browser-visible data.
- `src/linux_visible.py` - reused Linux visibility helper.
- `src/inventory_watcher.py` - reused long-running watcher for process and file exercises.
- `src/web/index.html` - new plain HTML inventory page.
- `src/web/app.js` - new browser JavaScript that fetches and renders inventory JSON.
- `src/web/style.css` - new minimal stylesheet for the browser lesson.
- `tests/test_http_server.py` - reused HTTP server tests that still prove the `/inventory` contract.
- `tests/test_inventory_cli.py` - reused CLI contract tests.
- `tests/test_inventory_watcher.py` - reused watcher tests.
- `tests/test_linux_visible.py` - reused Linux visibility tests.
- `tests/test_web_app.js` - new Node safety check for the browser JavaScript contract.

## Run the lesson
From this folder:
```bash
python3 src/http_server.py
TINYWMS_PORT=8080 python3 src/http_server.py
# then open http://127.0.0.1:8000/ in a browser
curl -i http://127.0.0.1:8000/inventory
curl -i http://127.0.0.1:8000/index.html
python3 src/inventory_cli.py data/inventory.json list
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `src/web/style.css` to change the table colors, restart the HTTP server, and reload the browser page to see the visual change immediately.
2. Change the table rendering in `src/web/app.js` to show the `unit` column in a different way, then refresh the page and compare the browser table with `curl http://127.0.0.1:8000/inventory`.
## Continuity note
- Inherited contract: the inventory JSON file, schema, CLI, Linux-visible helpers, and HTTP `GET /inventory` response remain valid and unchanged.
- Boundary changed in this stage: the browser becomes a new consumer of the same JSON contract and fetches inventory over HTTP instead of reading the file directly.

## Component assembly update
- Added: `src/web/index.html`, `src/web/app.js`, `src/web/style.css`, and `tests/test_web_app.js`.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/http_server.py`, `src/inventory_cli.py`, `src/linux_visible.py`, `src/inventory_watcher.py`, and the earlier Python tests are carried forward without contract changes.
- Replaced/evolved: `README.md` and `docs/architecture.md` are expanded to teach the browser boundary, the `GET /inventory` dependency, and visible failure handling in the page.

## Cleanup
If you started the HTTP server, stop it with `Ctrl+C`. No external resources are created in this stage.
