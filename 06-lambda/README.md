# TinyWMS lesson: 06-lambda

## Stage purpose
This stage adds an AWS Lambda implementation for `GET /inventory` without removing the Raspberry Pi and EC2 HTTP versions. The goal is to compare execution models and request/response boundaries while keeping the same inventory JSON contract.

## Files in this lesson
- `src/lambda_inventory.py` - Lambda handler that accepts a readable JSON event and returns a JSON response
- `src/lambda_event_example.json` - sample event students can inspect or pass to the handler
- `deploy/lambda/template.json` - minimal CloudFormation-style deployment example for the Lambda function
- `deploy/lambda/invoke.sh` - local helper that simulates an event and prints the Lambda response
- `docs/architecture.md` - compares Pi, EC2, and Lambda execution paths
- `docs/data-contracts.md` - documents the same inventory contract and the Lambda input/output shapes
- `tests/test_lambda_inventory.py` - tests for the Lambda handler and error handling

## Run the lesson
From this folder:
```bash
python3 src/lambda_inventory.py < src/lambda_event_example.json
```
Or use the helper script:
```bash
bash deploy/lambda/invoke.sh
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change the Lambda response to add a `source` field and update the test that checks the JSON body.
2. Edit `src/lambda_event_example.json` to simulate a missing path and observe the error message returned by the handler.

## Continuity note
- Inherited contract: `GET /inventory` still returns the same inventory JSON body used by the CLI, browser, Raspberry Pi, and EC2 stages
- Boundary changed in this stage: the compute boundary can now be Lambda instead of a long-running Linux process

## Cleanup
No external resources are created in this stage when running locally. If you deploy Lambda in AWS, delete the function and its CloudFormation stack to stop AWS charges.
