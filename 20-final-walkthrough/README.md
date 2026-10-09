# TinyWMS lesson: 20-final-walkthrough

## Stage purpose
This final stage gives students one end-to-end walkthrough of the complete TinyWMS architecture. It traces a single warehouse order across browser, HTTP, API Gateway, Lambda, RDS, SQS, EventBridge, and the Linux pick-ticket worker while keeping JSON, SQL, process, and AWS boundaries visible.

## Files in this lesson
- `README.md` - this lesson guide for reviewing the final architecture walkthrough
- `docs/end-to-end.md` - the main end-to-end trace showing each hop, boundary, failure mode, operator, and persistent state with Mermaid diagrams
- `docs/architecture.md` - updated architecture guide that now points to the final walkthrough as the best single-document map of the current system
- `docs/data-contracts.md` - updated contract guide that connects the established JSON contracts to the final walkthrough document
- `tests/test_end_to_end_doc.py` - tests that verify the walkthrough document covers the required components and teaching checkpoints

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

Read the final walkthrough:
```bash
cat docs/end-to-end.md
```

If you want a generated JSON trace to compare with the document examples:
```bash
python3 src/demo_trace.py --order-file data/order-example.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Open `docs/end-to-end.md` and pick one hop, such as API Gateway to Lambda or Lambda to SQS. Add one extra sentence explaining what exact JSON is crossing that boundary, then re-run the tests.
2. Use `python3 src/demo_trace.py --order-file data/order-example.json` and compare its output to `docs/end-to-end.md`. Update the walkthrough with one note about a failure path, such as what happens if RDS is unavailable or the worker cannot write `pick-tickets.txt`, then re-run the tests.

## Continuity note
- Inherited contract: `GET /inventory`, `POST /orders`, the inventory JSON, order JSON, `PickWorkRequested` message, `OrderPlaced` event, and pick-ticket text output all remain unchanged from the previous stage
- Boundary changed in this stage: no runtime component changed; the repository now adds a final architecture walkthrough that connects all existing boundaries into one readable trace

## Cleanup
No external resources are created in this stage.
