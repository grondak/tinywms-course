# TinyWMS lesson: 13-sqs

## Stage purpose
This stage introduces asynchronous work after a successful order commit. `POST /orders` still returns the same kind of order success JSON to the caller, but now the Lambda path also publishes a separate JSON pick-work message to Amazon SQS so pick processing can happen later in another process.

## Files in this lesson
- `src/order_service.py` - order handler now publishes a pick-work message after the database transaction succeeds
- `src/pick_work.py` - defines the pick-work JSON message contract and builds the message from a committed order result
- `src/sqs_publish.py` - small SQS publisher that uses visible AWS environment variables and prints the sent message ID
- `src/sqs_consumer.py` - simple polling consumer that receives one or more SQS messages, prints message metadata and JSON body, and optionally acknowledges them
- `data/pick-work-message-example.json` - example pick-work message students can inspect before touching AWS
- `docs/data-contracts.md` - documents the SQS message contract separately from the existing HTTP order contract
- `docs/architecture.md` - explains the new boundary from synchronous HTTP/database work to asynchronous queue-based work
- `deploy/sqs/template.json` - minimal CloudFormation for a teaching queue
- `deploy/sqs/send-example.sh` - sends the example pick-work message to SQS from the command line
- `deploy/sqs/receive.sh` - runs the Python consumer against the queue
- `tests/test_pick_work.py` - tests the message shape built from committed order data
- `tests/test_sqs_publish.py` - tests visible SQS publishing behavior without calling AWS
- `tests/test_sqs_consumer.py` - tests receive/acknowledgement behavior and retry visibility

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
python3 -m src.pick_work < data/pick-work-message-example.json
```

To publish a real queue message after creating an order through Lambda, set these environment variables before invoking the order path:
```bash
export TINYWMS_DB_HOST=127.0.0.1
export TINYWMS_DB_PORT=5432
export TINYWMS_DB_NAME=tinywms
export TINYWMS_DB_USER=tinywms
export TINYWMS_DB_PASSWORD=secret
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export AWS_REGION=us-east-1
python3 src/lambda_inventory.py < src/order_event_example.json
```
The order response still comes back immediately after the database commit. Pick work is placed onto SQS separately.

To consume messages from the queue:
```bash
export TINYWMS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/tinywms-pick-work
export AWS_REGION=us-east-1
python3 src/sqs_consumer.py --max-messages 1 --ack
```
Run without `--ack` to make retries visible:
```bash
python3 src/sqs_consumer.py --max-messages 1
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Edit `src/pick_work.py` to add a new top-level field such as `warehouse`. Update the tests and `docs/data-contracts.md`, then re-run the suite.
2. Run `python3 src/sqs_consumer.py --max-messages 1` without `--ack`, then run it again after the message visibility timeout expires. Explain why the same message can appear again and which code line controls acknowledgement.

## Continuity note
- Inherited contract: `GET /inventory` and `POST /orders` keep the same HTTP routes and JSON request/response meanings used by the browser and earlier Lambda tests
- Boundary changed in this stage: after a successful committed order, TinyWMS now crosses a new AWS boundary by publishing a JSON pick-work command message to Amazon SQS instead of doing downstream work synchronously inside the HTTP request

## Cleanup
Local automated tests do not create AWS resources. If you deploy the SQS queue, delete the CloudFormation stack or queue when finished to avoid small ongoing charges:
```bash
aws cloudformation delete-stack --stack-name tinywms-sqs
```
Also unset environment variables containing database or queue settings when you are done with a lab shell.
