# TinyWMS lesson: 05-ec2-deployment

## Stage purpose
This stage shows how the same TinyWMS HTTP application can run on Amazon EC2 Linux instead of a Raspberry Pi. The lesson focuses on SSH access, environment configuration, process startup, and keeping the JSON contract unchanged.

## Files in this lesson
- `deploy/ec2/start.sh` - example startup script that sets the port and launches the HTTP server
- `deploy/ec2/tinywms.service` - sample systemd unit for a Linux host
- `docs/architecture.md` - compares Raspberry Pi and EC2 deployment variants
- `src/http_server.py` - the unchanged HTTP application
- `data/inventory.json` - the unchanged JSON data file

## Run the lesson
From this folder on the server:
```bash
export TINYWMS_PORT=8000
python3 src/http_server.py data/inventory.json
```
Or via the sample start script:
```bash
bash deploy/ec2/start.sh
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change the port in `deploy/ec2/start.sh` and verify `curl` still reaches the same `/inventory` JSON.
2. Adapt the systemd unit for a different Linux username and explain why the contract does not change.

## Continuity note
- Inherited contract: the HTTP request/response behavior and the inventory JSON body remain unchanged
- Boundary changed in this stage: the runtime is now documented for EC2 Linux deployment alongside the Raspberry Pi

## Cleanup
Stop the service or background process before terminating the EC2 instance. AWS EC2 usage can incur compute and storage cost until the instance is stopped or terminated.
