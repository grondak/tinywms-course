#!/bin/sh
set -eu
export TINYWMS_PORT="${TINYWMS_PORT:-8000}"
exec python3 src/http_server.py data/inventory.json
