from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cv_rules.db"
SCHEMA = ROOT / "db" / "schema.sql"
SEED = ROOT / "db" / "seed_v1.sql"


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA.read_text())
        conn.executescript(SEED.read_text())
    print(f"Initialized rules database at: {DB_PATH}")


if __name__ == "__main__":
    main()
