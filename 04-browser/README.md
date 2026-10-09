# TinyWMS lesson: 04-browser

## Stage purpose
This stage adds a simple browser view for the same inventory JSON contract already served by HTTP. Students can trace the data flow from server JSON to `fetch()` to table rows without any frontend framework machinery.

## Files in this lesson
- `src/http_server.py` - serves the JSON API and the static browser page
- `src/web/index.html` - plain HTML user interface
- `src/web/app.js` - browser JavaScript that calls `fetch('/inventory')`
- `src/web/style.css` - tiny styling for readability
- `tests/test_http_server.py` - tests that the server still returns the inventory JSON

## Run the lesson
From this folder:
```bash
export TINYWMS_PORT=8000
python3 src/http_server.py data/inventory.json
```
Then open the browser page at:
```text
http://127.0.0.1:8000/
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change the table columns in `src/web/app.js` and reload the page.
2. Turn off the server and observe the browser error message when `fetch()` fails.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same JSON inventory document
- Boundary changed in this stage: a browser client now consumes the contract through `fetch()` and renders HTML

## Cleanup
Stop the server with `Ctrl+C`. No external resources are created in this stage.
