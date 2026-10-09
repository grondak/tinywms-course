#!/bin/sh
set -eu
python3 src/lambda_inventory.py < src/lambda_event_example.json
