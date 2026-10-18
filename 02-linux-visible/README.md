# TinyWMS lesson: 02-linux-visible

## Stage purpose
This stage keeps the JSON inventory backbone and adds tiny Linux-oriented demo programs so students can see stdin, stdout, stderr, exit codes, environment variables, files, and a long-running process in action. The point is to make process behavior visible with ordinary shell tools before HTTP arrives in the next stage.

## Files in this lesson
- `data/inventory.json` - reused Stage 1 inventory data for all examples in this lesson.
- `data/inventory.schema.json` - reused schema describing the inventory JSON contract.
- `docs/architecture.md` - updated Component Assembly Map showing the new Linux-observability tools and the Stage 1 components they reuse.
- `docs/data-contracts.md` - reused inventory contract notes.
- `src/inventory_cli.py` - reused CLI for listing, finding, and dumping inventory JSON.
- `src/linux_visible.py` - small command-line helper that makes stdin/stdout/stderr, exit codes, and environment variables visible.
- `src/inventory_watcher.py` - long-running process that repeatedly snapshots inventory JSON into a log file so students can use `tail -f`.
- `tests/test_inventory_cli.py` - reused inventory CLI tests from Stage 1.
- `tests/test_linux_visible.py` - new tests for the Linux-visible helper commands.
- `tests/test_inventory_watcher.py` - new tests for the watcher snapshot behavior.

## Run the lesson
From this folder:
```bash
python3 src/linux_visible.py env
TINYWMS_DEMO=hello python3 src/linux_visible.py env
printf 'widget\n' | python3 src/linux_visible.py echo
python3 src/linux_visible.py echo hello from argv
python3 src/linux_visible.py fail
python3 src/inventory_watcher.py data/inventory.json /tmp/tinywms-watch.log
```

## Run tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Student exercises
1. Change `TINYWMS_DEMO` and run `python3 src/linux_visible.py env`, then observe the new value printed on stdout.
2. Start `python3 src/inventory_watcher.py data/inventory.json /tmp/tinywms-watch.log` in one terminal, edit `data/inventory.json` in another, and use `tail -f /tmp/tinywms-watch.log` to watch the repeated snapshots.
## Continuity note
- Inherited contract: the inventory JSON file, schema, and CLI from Stage 1 remain valid and continue to define the data shape.
- Boundary changed in this stage: TinyWMS now exposes additional Linux process behavior through small demo tools, including stderr and exit codes, plus a long-running watcher process with a log file.

## Component assembly update
- Added: `src/linux_visible.py`, `src/inventory_watcher.py`, `tests/test_linux_visible.py`, `tests/test_inventory_watcher.py`.
- Reused unchanged: `data/inventory.json`, `data/inventory.schema.json`, `src/inventory_cli.py`, and `tests/test_inventory_cli.py` are carried forward exactly from Stage 1.
- Replaced/evolved: `README.md` and `docs/architecture.md` are expanded to teach Linux visibility and to document the new process/file boundaries.

## Cleanup
If you started the watcher, stop it with `Ctrl+C` and remove any temporary log file you created, for example `rm -f /tmp/tinywms-watch.log`.
