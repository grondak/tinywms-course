# TinyWMS lesson: 19-git-history

## Stage purpose
This stage teaches students how to read TinyWMS as a semester story in Git instead of pretending each lesson is a separate historical commit. The repository keeps the stage directories together in one checkout, so students can compare earlier and later lesson folders honestly without rewriting history or inventing tags.

## Files in this lesson
- `deploy/local/run_local.sh` - starts the system on one machine, no AWS needed
- `src/local_aws.py` - configures local mode and provides the directory-backed queue and event bus
- `tests/test_local_stack.py` - drives local mode over HTTP and runs the worker and event consumers
- `README.md` - lesson guide for the Git-history stage.
- `docs/git-history.md` - explanation of the repository’s stage-directory model and honest comparison commands.
- `docs/architecture.md` - updated component timeline derived from the existing assembly map.
- `data/inventory.json` - inherited inventory sample used by earlier stages.
- `data/inventory.schema.json` - inherited inventory schema.
- `data/orders.schema.json` - inherited order schema.
- `data/pick-work.json` - inherited pick-work command example.
- `data/schema.sql` - inherited relational schema.
- `data/seed.sql` - inherited relational seed data.
- `src/lambda_inventory.py` - inherited order/inventory handler used by later cloud stages.
- `src/pick_ticket_worker.py` - inherited worker used by the queue lesson and later demos.
- `infra/template.yaml` - consolidated cloud stack artifact from the AWS lesson.
- `tests/test_deployment_wiring.py` - inherited standard-library deployment wiring checks.

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

To inspect the history lesson text directly:
```bash
sed -n '1,220p' docs/git-history.md
```

To compare two lesson artifacts without inventing tags:
```bash
git diff --no-index deploy/pick-ticket-worker/README.md deploy/container-worker/README.md
```

## Run tests
```bash
node --test tests/test_web_app.js
```

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Student exercises
1. Open `docs/git-history.md`, pick two real stage artifacts, and run `git diff --no-index` on them so you can see how the queue, worker, and deployment lessons changed over time.
2. Compare `docs/architecture.md` to `docs/git-history.md`, then edit the history guide to add one more honest comparison command that uses existing paths from this checkout and observe the new text with `sed`.
## Continuity note
- Inherited contract: the inventory JSON, order JSON, pick-work command, OrderPlaced event, and pick-ticket output contracts remain unchanged.
- Boundary changed in this stage: history becomes part of the lesson artifact, so students now study stage directories and real file comparisons rather than imagined milestone tags.

## Component assembly update
- Added: `docs/git-history.md` as the new lesson artifact for comparing stages honestly.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `data/orders.schema.json`, `data/pick-work.json`, `data/schema.sql`, `data/seed.sql`, `src/lambda_inventory.py`, `src/pick_ticket_worker.py`, `infra/template.yaml`, and `tests/test_deployment_wiring.py` from earlier stages.
- Replaced/evolved: `README.md` and `docs/architecture.md` now include the Git-history lesson and a component-evolution timeline that points students at real stage paths.

## Cleanup
No external resources are created in this stage. If you make local comparison copies while experimenting, remove them when you are done.
