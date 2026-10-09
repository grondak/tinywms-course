# TinyWMS lesson: 17-container-worker

## Stage purpose
This stage packages only the existing pick-ticket worker into a Docker image. The goal is to show that the same Python Linux process can run either directly on a host or inside a container, while keeping environment variables, stdout/stderr, input JSON, and the persistent output file visible.

## Files in this lesson
- `Dockerfile.worker` - small Docker image definition for the pick-ticket worker
- `deploy/container/run-worker-container.sh` - helper script that runs the worker container with visible environment variables and a mounted output directory
- `src/pick_ticket_worker.py` - same worker logic as the previous stage, now also able to read its output path from an environment variable for container demos
- `docs/architecture.md` - updated to describe the worker container as an additional execution option without replacing the existing Linux process path
- `docs/data-contracts.md` - updated to note that containerization does not change the pick-work JSON or pick-ticket text contracts
- `tests/test_pick_ticket_worker.py` - expanded tests for the new environment-variable-driven output path behavior

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

Run the worker directly on the host as before:
```bash
rm -f pick-tickets.txt
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
cat pick-tickets.txt
```

Build the worker image:
```bash
docker build -f Dockerfile.worker -t tinywms-pick-ticket-worker:lesson .
```

Run one message through the worker in a container and persist output on the host:
```bash
rm -rf container-output
mkdir -p container-output
docker run --rm \
  -e TINYWMS_PICK_TICKETS_PATH=/work/output/pick-tickets.txt \
  -v "$(pwd)/container-output:/work/output" \
  tinywms-pick-ticket-worker:lesson \
  --once --message-file data/pick-work-message-example.json
cat container-output/pick-tickets.txt
```

Run the long-lived worker container against SQS with a mounted output volume:
```bash
mkdir -p container-output
docker run --rm \
  -e AWS_REGION=us-east-1 \
  -e TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work \
  -e TINYWMS_PICK_TICKETS_PATH=/work/output/pick-tickets.txt \
  -v "$(pwd)/container-output:/work/output" \
  tinywms-pick-ticket-worker:lesson \
  --poll-seconds 2
```

Watch the persistent output file from the host:
```bash
tail -f container-output/pick-tickets.txt
```

Or use the helper wrapper:
```bash
mkdir -p container-output
TINYWMS_PICK_TICKETS_PATH=/work/output/pick-tickets.txt \
./deploy/container/run-worker-container.sh --once --message-file data/pick-work-message-example.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `Dockerfile.worker` to add `ENV PYTHONUNBUFFERED=1`, rebuild the image, and compare the container log behavior with the host-run worker.
2. Change the mounted host directory from `container-output` to a new folder, rerun the container, and verify that the pick ticket appears in the new host path without changing the JSON message contract.

## Continuity note
- Inherited contract: the worker still consumes the same `PickWorkRequested` JSON message and still appends the same human-readable pick-ticket text
- Boundary changed in this stage: the worker can now run inside a Docker container image instead of only as a direct Linux host process

## Cleanup
Remove local output files:
```bash
rm -f pick-tickets.txt
rm -rf container-output
```
Stop and remove any running worker containers:
```bash
docker ps
docker stop <container-id>
```
Remove the lesson image when finished:
```bash
docker rmi tinywms-pick-ticket-worker:lesson
```
No AWS resources are created by this stage, but a live SQS polling demo may use already-existing resources from earlier lessons.
