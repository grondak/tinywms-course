#!/bin/sh
set -eu

: "${AWS_REGION:=us-east-1}"
: "${TINYWMS_STACK_NAME:?set TINYWMS_STACK_NAME}"
: "${TINYWMS_ARTIFACT_BUCKET:?set TINYWMS_ARTIFACT_BUCKET}"

aws cloudformation delete-stack \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME"

aws cloudformation wait stack-delete-complete \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME"

aws s3 rm "s3://$TINYWMS_ARTIFACT_BUCKET/lambda/${TINYWMS_STACK_NAME}-tinywms-lambda.zip" \
  --region "$AWS_REGION" || true

printf 'deleted stack=%s region=%s\n' "$TINYWMS_STACK_NAME" "$AWS_REGION"
