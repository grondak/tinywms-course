#!/usr/bin/env bash
# Run the whole TinyWMS system on this machine, no AWS needed:
#   web page + order API (the Lambda handler code) -> SQLite -> queue and event bus (directories) -> pick-ticket worker
#
#   bash deploy/local/run_local.sh            # start; Ctrl+C stops everything
#   bash deploy/local/run_local.sh --reset    # throw away the database, queued messages and tickets first
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ "${1:-}" = "--reset" ]; then
  rm -rf local-aws pick-tickets.txt
  echo "cleared local-aws and pick-tickets.txt"
fi

export TINYWMS_LOCAL=1
export TINYWMS_PORT="${TINYWMS_PORT:-8000}"
export TINYWMS_LOCAL_DIR="${TINYWMS_LOCAL_DIR:-$PWD/local-aws}"

# The worker runs in the background and writes pick-tickets.txt; --wait-time-seconds 2 keeps Ctrl+C responsive.
python3 -m src.pick_ticket_worker "$TINYWMS_LOCAL_DIR/pick-work" pick-tickets.txt \
  --state-file "$TINYWMS_LOCAL_DIR/pick-ticket-worker-state.json" --wait-time-seconds 2 &
worker=$!
trap 'kill "$worker" 2>/dev/null || true' EXIT

echo "open http://127.0.0.1:$TINYWMS_PORT/   (tickets: tail -f pick-tickets.txt)"
python3 src/http_server.py
