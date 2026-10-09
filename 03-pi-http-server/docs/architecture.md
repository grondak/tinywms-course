# TinyWMS architecture

## Current architecture
- TinyWMS now has a Python CLI that reads JSON inventory data.
- TinyWMS now has a small Python HTTP server that serves `GET /inventory`.
- The same inventory JSON contract is shared across both interfaces.

## Architecture History
- Stage 0: repository scaffold only.
- Stage 1: JSON inventory contract and CLI reader.
- Stage 2: Linux-visible command-line examples.
- Stage 3: Raspberry Pi / EC2-style HTTP server added while preserving the same inventory JSON.
