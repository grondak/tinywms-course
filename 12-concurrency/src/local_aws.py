"""Local mode: run the order API on one machine with SQLite instead of RDS.

TINYWMS_LOCAL=1 makes the HTTP server answer through the same handler code that
Lambda runs, against a SQLite file. This stage has no queue or event bus yet.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV = 'TINYWMS_LOCAL'
LOCAL_DIR_ENV = 'TINYWMS_LOCAL_DIR'


def local_dir() -> Path:
    return Path(os.environ.get(LOCAL_DIR_ENV, ROOT / 'local-aws'))


def configure() -> Path:
    """Point the app at SQLite and create the SQLite database on first use. Returns the state directory."""
    base = local_dir()
    base.mkdir(parents=True, exist_ok=True)
    os.environ[LOCAL_ENV] = '1'
    os.environ.setdefault('TINYWMS_DB', 'sqlite')
    os.environ.setdefault('TINYWMS_SQLITE_PATH', str(base / 'tinywms.db'))
    db_path = Path(os.environ['TINYWMS_SQLITE_PATH'])
    if os.environ['TINYWMS_DB'] == 'sqlite' and not db_path.exists():
        from data.init_db import init_db
        init_db()
    return base
