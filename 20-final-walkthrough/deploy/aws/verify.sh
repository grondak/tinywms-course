#!/bin/sh
set -eu

: "${AWS_REGION:=us-east-1}"
: "${TINYWMS_STACK_NAME:?set TINYWMS_STACK_NAME}"

aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output table

API_BASE_URL="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiBaseUrl`].OutputValue' \
  --output text)"

printf 'api base url: %s\n' "$API_BASE_URL"
printf 'try: curl %s/inventory\n' "$API_BASE_URL"
printf 'try: curl -X POST %s/orders -H '\''Content-Type: application/json'\'' -H '\''Accept: application/json'\'' --data @data/order-example.json\n' "$API_BASE_URL"

curl --fail "$API_BASE_URL/inventory"
