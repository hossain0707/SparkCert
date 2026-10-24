"""Minimal SQLite persistence. No credentials are ever stored."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, root: Path | str | None = None):
        self.root = Path(root or os.environ.get("SPARKCERT_HOME", Path.home() / ".sparkcert"))
        self.root.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            self.root.chmod(0o700)
        self.path = self.root / "sparkcert.db"
        self._init()

    def conn(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def _init(self):
        with self.conn() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, host TEXT NOT NULL,
                username TEXT NOT NULL DEFAULT '', port INTEGER NOT NULL DEFAULT 22,
                ssh_alias TEXT NOT NULL DEFAULT '', identity_file TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, device_id TEXT,
                device_name TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
                status TEXT NOT NULL, score REAL, result_json TEXT NOT NULL,
                FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE SET NULL
            )""")
        if os.name != "nt":
            self.path.chmod(0o600)

    def devices(self) -> list[dict]:
        with self.conn() as db:
            return [dict(r) for r in db.execute("SELECT * FROM devices ORDER BY updated_at DESC")]

    def device(self, id: str) -> dict | None:
        with self.conn() as db:
            row = db.execute("SELECT * FROM devices WHERE id=?", (id,)).fetchone()
            return dict(row) if row else None

    def add_device(self, fields: dict) -> dict:
        now = utcnow()
        record = {"id": str(uuid4()), **fields, "created_at": now, "updated_at": now}
        with self.conn() as db:
            db.execute("""INSERT INTO devices
                (id,name,host,username,port,ssh_alias,identity_file,created_at,updated_at)
                VALUES (:id,:name,:host,:username,:port,:ssh_alias,:identity_file,:created_at,:updated_at)
            """, record)
        return record

    def delete_device(self, id: str) -> bool:
        with self.conn() as db:
            cur = db.execute("DELETE FROM devices WHERE id=?", (id,))
            return cur.rowcount > 0

    def add_run(self, kind: str, result: dict, device_id: str | None = None, device_name: str = "") -> dict:
        rec = {"id": str(uuid4()), "kind": kind, "device_id": device_id,
               "device_name": device_name, "created_at": utcnow(),
               "status": result.get("status", "completed"),
               "score": result.get("score"), "result_json": json.dumps(result)}
        with self.conn() as db:
            db.execute("""INSERT INTO runs (id,kind,device_id,device_name,created_at,status,score,result_json)
                VALUES (:id,:kind,:device_id,:device_name,:created_at,:status,:score,:result_json)""", rec)
        return self.run(rec["id"])

    def runs(self, limit: int = 100) -> list[dict]:
        with self.conn() as db:
            rows = db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._run_dict(r) for r in rows]

    def run(self, id: str) -> dict | None:
        with self.conn() as db:
            row = db.execute("SELECT * FROM runs WHERE id=?", (id,)).fetchone()
        return self._run_dict(row) if row else None

    @staticmethod
    def _run_dict(row):
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json"))
        return item
