#!/bin/sh
set -eu
: "${TINYWMS_EVENT_BUS_NAME:?set TINYWMS_EVENT_BUS_NAME}"
export AWS_REGION="${AWS_REGION:-us-east-1}"
exec python3 src/eventbridge_publish.py data/order-placed-event-example.json
