# TinyWMS lesson: 17-container-worker

## Stage purpose
This stage shows the pick-ticket worker running inside Docker while keeping the same queue command contract and durable ticket/idempotency state from the earlier Linux and systemd lessons. The point is to teach containers as a new runtime wrapper for the same worker process, not to redesign TinyWMS.

## Files in this lesson
- `README.md` - lesson guide for building, running, testing, and observing the containerized worker.
- `docs/architecture.md` - updated component map showing the container runtime as an alternate worker execution environment.
- `deploy/container-worker/README.md` - operator guide with exact `docker build` and `docker run` commands, mounts, and cleanup steps.
- `src/Dockerfile` - image definition for the worker process and its default command.
- `tests/test_container_worker.py` - checks the Dockerfile, the deploy guide, and the worker entrypoint/arguments contract.
- `src/pick_ticket_worker.py` - reused worker process that still owns the queue-to-ticket behavior.
- `src/sqs_consumer.py` - reused queue receive/delete helper used by the worker.

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
