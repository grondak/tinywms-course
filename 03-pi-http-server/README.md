# TinyWMS lesson: 03-pi-http-server

## Stage purpose
This stage adds the first TinyWMS HTTP server. Students can see a live process listening on a port, serving a JSON response, and returning an HTTP status code and headers from the same inventory contract used by the CLI.

## Files in this lesson
- `src/http_server.py` - small Python HTTP server with `GET /inventory`
- `src/inventory_cli.py` - still available for direct JSON inspection
- `data/inventory.json` - shared inventory data source
- `tests/test_http_server.py` - request/response tests against the HTTP handler
- `docs/architecture.md` - records the new Pi-style server boundary

## Run the lesson
From this folder:
```bash
export TINYWMS_PORT=8000
python3 src/http_server.py data/inventory.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change `TINYWMS_PORT` and re-run the server to see that the listener moves without changing the JSON contract.
2. Use `curl -i http://127.0.0.1:8000/inventory` and compare the headers with the response body.

## Continuity note
- Inherited contract: the inventory JSON document stays the same as the CLI version
- Boundary changed in this stage: TinyWMS now crosses an HTTP request/response boundary on the Raspberry Pi or EC2 Linux

## Cleanup
Stop the server with `Ctrl+C`. No external resources are created in this stage.
