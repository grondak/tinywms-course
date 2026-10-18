# TinyWMS lesson: 19-git-history

## Stage purpose
This stage teaches students how to read TinyWMS as a semester story in Git instead of pretending each lesson is a separate historical commit. The repository keeps the stage directories together in one checkout, so students can compare earlier and later lesson folders honestly without rewriting history or inventing tags.

## Files in this lesson
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
