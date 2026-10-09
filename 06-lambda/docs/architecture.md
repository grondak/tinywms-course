# TinyWMS architecture

## Current architecture
- TinyWMS has a Python CLI that reads JSON inventory data.
- TinyWMS has a small Python HTTP server that serves `GET /inventory`.
- TinyWMS now also has a Lambda handler that can return the same inventory JSON without running a long-lived Linux web server.
- The same inventory JSON contract is shared across CLI, browser, Raspberry Pi Linux, EC2 Linux, and Lambda.

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

### What stayed the same
- The inventory JSON contract stayed the same.
- The `/inventory` meaning stayed the same even though the compute model changed.
- The browser client can still consume the same JSON without changes.

## Architecture History
- Stage 0: repository scaffold only.
- Stage 1: JSON inventory contract and CLI reader.
- Stage 2: Linux-visible command-line examples.
- Stage 3: Raspberry Pi / EC2-style HTTP server added.
- Stage 4: browser client added.
- Stage 5: EC2 deployment scripts and documentation added without changing the app contract.
- Stage 6: Lambda implementation added alongside the existing Linux server path.
