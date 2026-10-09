#!/usr/bin/env python3
import os
import sys
import zipfile
from pathlib import Path

INCLUDE_FILES = [
    "src/lambda_inventory.py",
    "src/order_service.py",
    "src/rds_inventory.py",
    "src/pick_work.py",
    "src/domain_events.py",
    "src/sqs_publish.py",
    "src/eventbridge_publish.py",
]

INCLUDE_DIRECTORIES = [
    "src",
]

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

EXCLUDE_PARTS = {
    "__pycache__",
}


def should_include(path):
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def add_tree(zip_file, root_dir):
    root_path = Path(root_dir)
    for path in sorted(root_path.rglob("*")):
        if should_include(path):
            zip_file.write(path, arcname=str(path))


def main(argv):
    if len(argv) != 2:
        print("usage: package_lambda.py <output.zip>", file=sys.stderr)
        return 2

    output_path = Path(argv[1])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        written = set()
        for file_name in INCLUDE_FILES:
            path = Path(file_name)
            if should_include(path):
                zf.write(path, arcname=str(path))
                written.add(str(path))
        for directory in INCLUDE_DIRECTORIES:
            root_path = Path(directory)
            for path in sorted(root_path.rglob("*")):
                if should_include(path) and str(path) not in written:
                    zf.write(path, arcname=str(path))
                    written.add(str(path))

    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
