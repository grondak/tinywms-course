#!/usr/bin/env bash
# Run the whole TinyWMS system on this machine, no AWS needed:
#   web page + order API (the Lambda handler code) -> SQLite
#
#   bash deploy/local/run_local.sh            # start; Ctrl+C stops everything
#   bash deploy/local/run_local.sh --reset    # throw away the database first
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ "${1:-}" = "--reset" ]; then
  rm -rf local-aws
  echo "cleared local-aws"
fi

export TINYWMS_LOCAL=1
export TINYWMS_PORT="${TINYWMS_PORT:-8000}"
export TINYWMS_LOCAL_DIR="${TINYWMS_LOCAL_DIR:-$PWD/local-aws}"

echo "open http://127.0.0.1:$TINYWMS_PORT/"
python3 src/http_server.py
