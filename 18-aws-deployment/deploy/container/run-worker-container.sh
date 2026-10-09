#!/bin/sh
set -eu

IMAGE_NAME="${TINYWMS_WORKER_IMAGE:-tinywms-pick-ticket-worker:lesson}"
OUTPUT_DIR="${TINYWMS_CONTAINER_OUTPUT_DIR:-$(pwd)/container-output}"
OUTPUT_PATH="${TINYWMS_PICK_TICKETS_PATH:-/work/output/pick-tickets.txt}"

mkdir -p "$OUTPUT_DIR"

exec docker run --rm \
  -e "AWS_REGION=${AWS_REGION:-us-east-1}" \
  -e "TINYWMS_SQS_QUEUE_URL=${TINYWMS_SQS_QUEUE_URL:-}" \
  -e "TINYWMS_PICK_TICKETS_PATH=$OUTPUT_PATH" \
  -v "$OUTPUT_DIR:/work/output" \
  "$IMAGE_NAME" \
  "$@"
