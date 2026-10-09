#!/bin/sh
set -eu
: "${TINYWMS_SQS_QUEUE_URL:?set TINYWMS_SQS_QUEUE_URL}"
export AWS_REGION="${AWS_REGION:-us-east-1}"
exec python3 src/pick_ticket_worker.py --poll-seconds 2 --output pick-tickets.txt
