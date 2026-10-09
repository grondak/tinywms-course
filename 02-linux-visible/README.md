# TinyWMS lesson: 02-linux-visible

## Stage purpose
This stage turns the TinyWMS inventory data into small Linux-friendly programs that expose stdin, stdout, stderr, exit codes, files, environment variables, and a long-running process. Students can inspect these behaviors with ordinary shell tools before any HTTP server appears.

## Files in this lesson
- `src/inventory_cli.py` - the JSON inventory reader from the previous stage
- `src/linux_demo.py` - command-line examples that print to stdout/stderr, read stdin, and respect environment variables
- `src/watch_inventory.py` - a simple long-running process that repeatedly reports inventory file changes
- `tests/test_linux_demo.py` - tests for CLI exit codes and visible output
- `data/inventory.json` - sample data used by the exercises

## Run the lesson
From this folder:
```bash
python3 src/linux_demo.py stdout
python3 src/linux_demo.py stderr
python3 src/linux_demo.py stdin < data/inventory.json
DEMO_MESSAGE='hello from env' python3 src/linux_demo.py env
python3 src/watch_inventory.py data/inventory.json
```

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Pipe the inventory file through `grep SKU-1002` and explain why the line appears or not.
2. Start `watch_inventory.py`, edit `data/inventory.json`, and use `tail -f` in another terminal to watch the changes.

## Continuity note
- Inherited contract: the inventory JSON format and the CLI validation behavior remain unchanged
- Boundary changed in this stage: Linux process behavior is now part of the lesson, but there is still no HTTP server

## Cleanup
Stop any background `watch_inventory.py` processes with `kill <pid>` when you are done.
