# TinyWMS Architecture

## Current architecture

TinyWMS now has two visible teaching boundaries: the Stage 1 inventory JSON contract and CLI, plus Stage 2 Linux-visible demo tools that expose stdin, stdout, stderr, exit codes, environment variables, and a long-running file-writing process. The inventory JSON contract remains the canonical data shape; the new tools reuse it rather than replacing it.

## Architecture History

- Stage 0: repository scaffold only.
- Stage 1: inventory JSON contract and CLI backbone added.
- Stage 2: Linux-visible demo tools added to make shell, file, and process behavior observable.

## Component Assembly Map

| component name | stage introduced | runtime location | inbound contract | outbound contract | dependencies |
| --- | --- | --- | --- | --- | --- |
| inventory JSON file | 01-json-backbone | filesystem (`data/inventory.json`) | none | inventory JSON | none |
| inventory CLI | 01-json-backbone | Linux Python process (`src/inventory_cli.py`) | inventory JSON | printed list output, JSON dump, exit code | inventory JSON file |
| Linux-visible helper | 02-linux-visible | Linux Python process (`src/linux_visible.py`) | stdin, argv, environment variables | stdout, stderr, exit code | standard library, shell-provided stdin/stdout/stderr |
| inventory watcher | 02-linux-visible | Linux Python process (`src/inventory_watcher.py`) | inventory JSON file path, log-file path | repeated JSON snapshots in log file, visible long-running process | inventory JSON file, filesystem append access |
