#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path


def main(argv):
    if len(argv) < 2:
        print("usage: watch_inventory.py <inventory.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    last = None
    while True:
        current = path.read_text(encoding="utf-8")
        if current != last:
            data = json.loads(current)
            print(json.dumps(data, indent=2, sort_keys=True), flush=True)
            last = current
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
