#!/usr/bin/env python3
import json
import os
import sys


def main(argv):
    if len(argv) < 2:
        print("usage: linux_demo.py <stdout|stderr|stdin|env>", file=sys.stderr)
        return 2
    mode = argv[1]
    if mode == "stdout":
        print("TinyWMS stdout is visible")
        return 0
    if mode == "stderr":
        print("TinyWMS stderr is visible", file=sys.stderr)
        return 0
    if mode == "stdin":
        payload = sys.stdin.read()
        print(payload)
        return 0
    if mode == "env":
        print(os.environ.get("DEMO_MESSAGE", "DEMO_MESSAGE is not set"))
        return 0
    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
