#!/bin/sh
set -eu

: "${AWS_REGION:=us-east-1}"
: "${TINYWMS_STACK_NAME:?set TINYWMS_STACK_NAME}"
: "${TINYWMS_ARTIFACT_BUCKET:?set TINYWMS_ARTIFACT_BUCKET}"

PARAMETERS_FILE="${1:-deploy/aws/parameters.example.json}"
ARTIFACT_DIR="build"
ZIP_PATH="$ARTIFACT_DIR/tinywms-lambda.zip"
S3_KEY="lambda/${TINYWMS_STACK_NAME}-tinywms-lambda.zip"

mkdir -p "$ARTIFACT_DIR"
python3 deploy/aws/package_lambda.py "$ZIP_PATH"

aws s3 cp "$ZIP_PATH" "s3://$TINYWMS_ARTIFACT_BUCKET/$S3_KEY" --region "$AWS_REGION"

aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --template-file deploy/aws/template.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides file://"$PARAMETERS_FILE" \
  --no-fail-on-empty-changeset

printf 'deployed stack=%s region=%s\n' "$TINYWMS_STACK_NAME" "$AWS_REGION"
printf 'lambda artifact=s3://%s/%s\n' "$TINYWMS_ARTIFACT_BUCKET" "$S3_KEY"
