# TinyWMS lesson: 17-container-worker

## Stage purpose
This stage shows the pick-ticket worker running inside Docker while keeping the same queue command contract and durable ticket/idempotency state from the earlier Linux and systemd lessons. The point is to teach containers as a new runtime wrapper for the same worker process, not to redesign TinyWMS.

## Files in this lesson
- `deploy/local/run_local.sh` - starts the system on one machine, no AWS needed
- `src/local_aws.py` - configures local mode and provides the directory-backed queue and event bus
- `tests/test_local_stack.py` - drives local mode over HTTP and runs the worker and event consumers
- `README.md` - lesson guide for building, running, testing, and observing the containerized worker.
- `docs/architecture.md` - updated component map showing the container runtime as an alternate worker execution environment.
- `deploy/container-worker/README.md` - operator guide with exact `docker build` and `docker run` commands, mounts, and cleanup steps.
- `src/Dockerfile` - image definition for the worker process and its default command.
- `tests/test_container_worker.py` - checks the Dockerfile, the deploy guide, and the worker entrypoint/arguments contract.
- `src/pick_ticket_worker.py` - reused worker process that still owns the queue-to-ticket behavior.
- `src/sqs_consumer.py` - reused queue receive/delete helper used by the worker.

## Run the whole system on your own machine
No AWS account needed. One command starts the web page, the order API (the same handler code Lambda runs), a SQLite database, a queue, an event bus and the pick-ticket worker:
```bash
bash deploy/local/run_local.sh            # add --reset to start from a clean database
# open http://127.0.0.1:8000/ , submit an order, then in a second terminal:
tail -f pick-tickets.txt
ls local-aws/pick-work local-aws/event-consumer-a      # the queue and the event, as files
export TINYWMS_LOCAL=1
python3 src/event_consumer_a.py local-aws/event-consumer-a
```
How it maps to the cloud design: the SQLite file stands in for RDS, each directory under `local-aws/` is an SQS queue (one JSON file per message), the event bus copies each event into `event-consumer-a` and `event-consumer-b` like the two EventBridge rules in `infra/events.yaml`, and `TINYWMS_LOCAL=1` is the only switch. Real SQS keeps a message hidden while a worker handles it and may deliver it twice; the file queue does neither, so the duplicate and retry lessons still need the tests or the cloud stack.

## Run the lesson
From the repository root:
```bash
python3 -m unittest discover -s tests -v
```

To inspect the container image directly:
```bash
docker build -f src/Dockerfile -t tinywms-pick-ticket-worker .
```

## Run tests
```bash
node --test tests/test_web_app.js
```

```bash
python3 -m unittest discover -s tests -v
```

## Student exercises
1. Change the worker formatting in `src/pick_ticket_worker.py`, rebuild the image, and run the container once to see the new ticket line appear in the mounted `pick-tickets.txt` file.
2. Edit the default command in `src/Dockerfile` or the run command in `deploy/container-worker/README.md`, then rebuild and run the bounded `--once` example to observe how Docker passes arguments to the worker process.
## Continuity note
- Inherited contract: the pick-work command JSON, pick-ticket output, and worker idempotency behavior remain valid.
- Boundary changed in this stage: the same worker process can now run inside a Docker container with explicit image, container, environment-variable, and volume boundaries.

## Component assembly update
- Added: `src/Dockerfile`, `deploy/container-worker/README.md`, and `tests/test_container_worker.py` as the container lesson artifacts.
- Reused unchanged: `src/pick_ticket_worker.py`, `src/sqs_consumer.py`, `docs/architecture.md` component names from earlier stages, and the existing pick-work/pick-ticket contracts.
- Replaced/evolved: the worker runtime is now documented as containerized in addition to the bare Linux and systemd paths; the worker logic itself is unchanged.

## Cleanup
```bash
docker rmi tinywms-pick-ticket-worker
rm -f deploy/container-worker/pick-tickets.txt deploy/container-worker/pick-ticket-worker-state.json
```
