# TinyWMS lesson: 18-aws-deployment

## Stage purpose
This stage makes the current TinyWMS cloud architecture reproducibly deployable on AWS with infrastructure as code. Students can now create the API Gateway + Lambda + RDS + SQS + EventBridge path as a repeatable stack, while still keeping the Raspberry Pi or any Linux host as a supported pick-ticket worker target that consumes the cloud queue and writes a local file.

## Files in this lesson
- `deploy/aws/template.json` - main CloudFormation template for VPC, subnets, security groups, RDS, SQS, EventBridge, IAM, Lambda, API Gateway, and CloudWatch logging
- `deploy/aws/package_lambda.py` - small Python packager that zips the Lambda source tree using only the standard library
- `deploy/aws/deploy.sh` - end-to-end helper that packages code, uploads artifacts to S3, and deploys the CloudFormation stack
- `deploy/aws/verify.sh` - prints stack outputs and runs simple HTTP verification commands against the deployed API
- `deploy/aws/destroy.sh` - explicit teardown helper for deleting the CloudFormation stack and the deployment S3 bucket contents
- `deploy/aws/parameters.example.json` - example stack parameters without committed secrets
- `deploy/aws/bootstrap_rds.sh` - applies the TinyWMS SQL schema and seed data to the deployed RDS instance
- `deploy/aws/pi-worker-env.example` - example environment file for a Raspberry Pi or Linux host running the worker against the deployed AWS queue
- `docs/architecture.md` - updated architecture guide describing the reproducible AWS deployment boundary and Raspberry Pi participation in the cloud system
- `docs/data-contracts.md` - updated to note that the new infrastructure packaging does not change the visible JSON contracts
- `tests/test_aws_deployment_files.py` - tests that validate the deployable artifact shapes and important CloudFormation wiring

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

Package the Lambda artifact locally:
```bash
python3 deploy/aws/package_lambda.py build/tinywms-lambda.zip
python3 -m zipfile -l build/tinywms-lambda.zip
```

Create an S3 bucket for deployment artifacts if you do not already have one:
```bash
export AWS_REGION=us-east-1
export TINYWMS_STACK_NAME=tinywms-lesson
export TINYWMS_ARTIFACT_BUCKET=tinywms-artifacts-123456789012-us-east-1
aws s3 mb s3://$TINYWMS_ARTIFACT_BUCKET --region $AWS_REGION
```

Copy the example parameters and edit them for your account, subnets, and database password:
```bash
cp deploy/aws/parameters.example.json deploy/aws/parameters.local.json
```

Deploy the stack:
```bash
export AWS_REGION=us-east-1
export TINYWMS_STACK_NAME=tinywms-lesson
export TINYWMS_ARTIFACT_BUCKET=tinywms-artifacts-123456789012-us-east-1
./deploy/aws/deploy.sh deploy/aws/parameters.local.json
```

After the stack finishes, inspect outputs:
```bash
./deploy/aws/verify.sh
```

Bootstrap the database schema and seed data into RDS:
```bash
export TINYWMS_DB_PASSWORD=replace-with-your-real-password
./deploy/aws/bootstrap_rds.sh
```

Verify the deployed API manually:
```bash
API_BASE_URL=$(aws cloudformation describe-stacks \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiBaseUrl`].OutputValue' \
  --output text)

curl "$API_BASE_URL/inventory"
curl -X POST "$API_BASE_URL/orders" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  --data @data/order-example.json
```

Run the Raspberry Pi or Linux worker against the deployed SQS queue:
```bash
QUEUE_URL=$(aws cloudformation describe-stacks \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`PickWorkQueueUrl`].OutputValue' \
  --output text)

export AWS_REGION=us-east-1
export TINYWMS_SQS_QUEUE_URL="$QUEUE_URL"
python3 src/pick_ticket_worker.py --poll-seconds 2 --output pick-tickets.txt
```

Watch the physical or Linux-host output file:
```bash
tail -f pick-tickets.txt
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Change the CloudFormation parameter `DbInstanceClass` from `db.t3.micro` to another inexpensive class in `deploy/aws/parameters.local.json`, redeploy, and inspect which parts of the application contract stayed the same even though infrastructure changed.
2. Edit `deploy/aws/template.json` to change the Lambda log retention period, redeploy, and verify with the AWS CLI that observability configuration changed without changing `GET /inventory` or `POST /orders` JSON behavior.

## Continuity note
- Inherited contract: `GET /inventory`, `POST /orders`, the `PickWorkRequested` SQS message, the `OrderPlaced` EventBridge event, and the worker’s human-readable pick-ticket output all remain compatible
- Boundary changed in this stage: the cloud-side architecture is now reproducibly described and deployed with CloudFormation and packaging scripts instead of being assembled from separate ad hoc resources

## Cleanup
This stage creates AWS resources that can cost money, especially RDS, NAT-free VPC infrastructure, API Gateway, Lambda, SQS, CloudWatch logs, and S3 artifact storage.

Delete the TinyWMS stack:
```bash
export AWS_REGION=us-east-1
export TINYWMS_STACK_NAME=tinywms-lesson
export TINYWMS_ARTIFACT_BUCKET=tinywms-artifacts-123456789012-us-east-1
./deploy/aws/destroy.sh
```

If you created the deployment artifact bucket only for this lesson, remove it after the stack is gone:
```bash
aws s3 rb "s3://$TINYWMS_ARTIFACT_BUCKET" --force
```

Stop any local or Raspberry Pi workers with `Ctrl+C` and remove local output files if desired:
```bash
rm -f pick-tickets.txt
rm -rf build
```

Never commit edited parameter files that contain real passwords or account-specific values.
