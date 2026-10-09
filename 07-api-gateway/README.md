# TinyWMS lesson: 07-api-gateway

## Stage purpose
This stage puts API Gateway in front of the existing Lambda inventory handler. The same `GET /inventory` JSON contract is now reachable through either the older Pi/EC2 HTTP server or the new API Gateway → Lambda path.

## Files in this lesson
- `src/lambda_inventory.py` - Lambda handler that still returns the inventory JSON contract
- `deploy/apigateway/template.json` - readable infrastructure template for API Gateway in front of Lambda
- `deploy/apigateway/invoke.sh` - local helper for showing the request path and Lambda response
- `src/web/index.html` - browser page, now able to choose a local HTTP base URL or an API Gateway base URL
- `src/web/app.js` - browser code that fetches inventory from a configurable endpoint
- `docs/architecture.md` - documents the new HTTP boundary and how API Gateway changes the path
- `docs/data-contracts.md` - records the HTTP/API Gateway request and response shapes students should inspect
- `tests/test_web_app.js` - browser-side logic tests for URL selection and fetch behavior

## Run the lesson
From this folder:
```bash
python3 src/http_server.py data/inventory.json
```
In another shell, open the browser page from the server and point it at the API Gateway URL when deployed.

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change the browser default so it starts with the API Gateway URL, then verify that the local Pi/EC2 server still works when you switch it back.
2. Break the `/inventory` path in `src/lambda_inventory.py` on purpose and observe the exact JSON error returned through API Gateway.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same inventory JSON body used by the CLI, browser, Raspberry Pi, EC2, and Lambda stages
- Boundary changed in this stage: API Gateway now becomes the HTTP front door in front of Lambda, while the older direct HTTP server remains available

## Cleanup
No external resources are created when running the local lesson. If you deploy API Gateway in AWS, delete the API, stage, and Lambda stack to stop charges.
