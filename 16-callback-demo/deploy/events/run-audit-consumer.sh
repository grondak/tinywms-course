#!/bin/sh
set -eu
exec python3 src/event_consumer_audit.py < data/order-placed-event-example.json
