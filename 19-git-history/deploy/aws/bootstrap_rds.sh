#!/bin/sh
set -eu

: "${AWS_REGION:=us-east-1}"
: "${TINYWMS_STACK_NAME:?set TINYWMS_STACK_NAME}"
: "${TINYWMS_DB_PASSWORD:?set TINYWMS_DB_PASSWORD}"

DB_HOST="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`DbEndpointAddress`].OutputValue' \
  --output text)"
DB_PORT="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`DbEndpointPort`].OutputValue' \
  --output text)"
DB_NAME="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseName`].OutputValue' \
  --output text)"
DB_USER="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$TINYWMS_STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseUser`].OutputValue' \
  --output text)"

export PGPASSWORD="$TINYWMS_DB_PASSWORD"

psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f deploy/rds/bootstrap.sql
