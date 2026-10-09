#!/bin/sh
set -eu
exec python3 src/demo_trace.py --order-file data/order-example.json
