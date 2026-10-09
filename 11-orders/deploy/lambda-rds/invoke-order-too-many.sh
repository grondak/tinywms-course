#!/bin/sh
set -eu
: "${TINYWMS_DB_HOST:?set TINYWMS_DB_HOST}"
: "${TINYWMS_DB_USER:?set TINYWMS_DB_USER}"
: "${TINYWMS_DB_PASSWORD:?set TINYWMS_DB_PASSWORD}"
export TINYWMS_DB_PORT="${TINYWMS_DB_PORT:-5432}"
export TINYWMS_DB_NAME="${TINYWMS_DB_NAME:-tinywms}"

python3 src/lambda_inventory.py < src/order_bad_event_example.json
