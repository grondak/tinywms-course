# TinyWMS architecture

## Current architecture
- TinyWMS has a Python CLI that reads JSON inventory data.
- TinyWMS has a small Python HTTP server that serves `GET /inventory`.
- TinyWMS has a Lambda handler that can return the same inventory JSON without running a long-lived Linux web server.
- TinyWMS now also has API Gateway in front of Lambda for the HTTP request path.
- The same inventory JSON contract is shared across CLI, browser, Raspberry Pi Linux, EC2 Linux, Lambda, and API Gateway.

## Deployment variants
### Raspberry Pi Linux
- Students can run the server directly on a Pi.
- They are responsible for the process, port, and OS updates.

### EC2 Linux
- Students can run the same server on an EC2 instance.
- They are responsible for the instance, SSH access, process startup, and port exposure.
- AWS is responsible for the data center, physical host, and basic cloud infrastructure beneath the instance.

### Lambda
- Students can upload the same inventory logic as a Lambda function.
- AWS starts the function for each request instead of the student running a persistent server process.
- Students are responsible for the function code, handler, and event shape.
- AWS is responsible for the execution environment and invocation service.

### API Gateway in front of Lambda
- Students can place API Gateway in front of the same Lambda inventory handler.
- API Gateway is responsible for exposing the HTTP route and translating the inbound request into a Lambda event.
- Students are still responsible for the URL path, method mapping, integration, and response contract.
- The Lambda function still owns the inventory JSON body.

### What stayed the same
- The inventory JSON contract stayed the same.
- The `/inventory` meaning stayed the same even though the compute and HTTP front door changed.
- The browser client can still consume the same JSON without changing its inventory model.

## Architecture History
- Stage 0: repository scaffold only.
- Stage 1: JSON inventory contract and CLI reader.
- Stage 2: Linux-visible command-line examples.
- Stage 3: Raspberry Pi / EC2-style HTTP server added.
- Stage 4: browser client added.
- Stage 5: EC2 deployment scripts and documentation added without changing the app contract.
- Stage 6: Lambda implementation added alongside the existing Linux server path.
- Stage 7: API Gateway added in front of Lambda without changing the inventory contract.
