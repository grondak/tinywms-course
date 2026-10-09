# TinyWMS lesson: 15-pick-ticket-worker

## Stage purpose
This stage turns the earlier SQS message consumer into a pick-ticket worker. Given a `PickWorkRequested` JSON message, the worker produces a human-readable warehouse pick ticket and appends it to `pick-tickets.txt` so students can watch a long-lived Linux process turn queue JSON into a local file.

## Files in this lesson
- `src/pick_ticket_worker.py` - long-running worker that receives SQS messages, prints visible logs to stdout/stderr, formats pick tickets, appends them to a text file, and optionally acknowledges messages
- `src/pick_ticket.py` - small formatter that converts a pick-work JSON message plus product/bin lookup rows into human-readable pick-ticket text
- `deploy/sqs/run-pick-ticket-worker.sh` - simple shell wrapper for running the worker as a visible Linux process
- `deploy/sqs/tinywms-pick-ticket-worker.service` - example systemd unit showing how the same Python worker can run as a restartable Linux service
- `docs/data-contracts.md` - now documents the human-readable pick-ticket file output created from the existing pick-work command
- `docs/architecture.md` - explains that the queue consumer has evolved into a file-writing worker process
- `tests/test_pick_ticket.py` - tests pick-ticket formatting from JSON command data plus inventory lookup rows
- `tests/test_pick_ticket_worker.py` - tests successful ticket writing, logging, file append behavior, and message acknowledgement wiring

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
python3 src/pick_ticket.py data/pick-work-message-example.json
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
cat pick-tickets.txt
```

To run the worker as a long-lived Linux process against SQS:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export AWS_REGION=us-east-1
python3 src/pick_ticket_worker.py --poll-seconds 2 --output pick-tickets.txt
```

To stop the long-lived worker:
```bash
Ctrl+C
```
The worker prints a shutdown message before exiting.

To run it through the provided shell wrapper:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
./deploy/sqs/run-pick-ticket-worker.sh
```

To install it as a Linux service on a host such as Raspberry Pi or EC2:
```bash
sudo cp deploy/sqs/tinywms-pick-ticket-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tinywms-pick-ticket-worker
sudo systemctl start tinywms-pick-ticket-worker
sudo systemctl status tinywms-pick-ticket-worker
journalctl -u tinywms-pick-ticket-worker -f
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Change `src/pick_ticket.py` so each line also prints the unit of measure, then update or extend the tests and re-run them.
2. Modify `src/pick_ticket_worker.py` so stderr logs include a short prefix such as `worker error:` on failed messages, then re-run `tests/test_pick_ticket_worker.py`.

## Continuity note
- Inherited contract: `GET /inventory`, `POST /orders`, the SQS `PickWorkRequested` command, and the EventBridge `OrderPlaced` event all remain valid
- Boundary changed in this stage: the earlier visible queue consumer is now a worker that performs real downstream work by converting the existing pick-work JSON command into a human-readable Linux file named `pick-tickets.txt`

## Cleanup
Local tests and local `--message-file` runs only create `pick-tickets.txt`, which you can remove with:
```bash
rm -f pick-tickets.txt
```
If you installed the Linux service for practice, stop and remove it when finished:
```bash
sudo systemctl stop tinywms-pick-ticket-worker
sudo systemctl disable tinywms-pick-ticket-worker
sudo rm -f /etc/systemd/system/tinywms-pick-ticket-worker.service
sudo systemctl daemon-reload
```
If you also deployed the SQS stack, delete it when you are done with the lab:
```bash
aws cloudformation delete-stack --stack-name tinywms-sqs
```
