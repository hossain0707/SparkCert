"""Minimal SQLite persistence. No credentials are ever stored."""
from __future__ import annotations

import json
import hashlib
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
            columns = {row[1] for row in db.execute("PRAGMA table_info(runs)")}
            if "result_sha256" not in columns:
                db.execute("ALTER TABLE runs ADD COLUMN result_sha256 TEXT")
            db.execute("""CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
                detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
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
        self.audit("device_added", record["id"])
        return record

    def delete_device(self, id: str) -> bool:
        with self.conn() as db:
            cur = db.execute("DELETE FROM devices WHERE id=?", (id,))
            deleted = cur.rowcount > 0
        if deleted:
            self.audit("device_removed", id)
        return deleted

    def add_run(self, kind: str, result: dict, device_id: str | None = None, device_name: str = "") -> dict:
        rec = {"id": str(uuid4()), "kind": kind, "device_id": device_id,
               "device_name": device_name, "created_at": utcnow(),
               "status": result.get("status", "completed"),
               "score": result.get("score"), "result_json": json.dumps(result)}
        rec["result_sha256"] = hashlib.sha256(rec["result_json"].encode("utf-8")).hexdigest()
        with self.conn() as db:
            db.execute("""INSERT INTO runs (id,kind,device_id,device_name,created_at,status,score,result_json,result_sha256)
                VALUES (:id,:kind,:device_id,:device_name,:created_at,:status,:score,:result_json,:result_sha256)""", rec)
        self.audit("assessment_saved", rec["id"])
        return self.run(rec["id"])

    def runs(self, limit: int = 100) -> list[dict]:
        with self.conn() as db:
            rows = db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._run_dict(r) for r in rows]

    def run(self, id: str) -> dict | None:
        with self.conn() as db:
            row = db.execute("SELECT * FROM runs WHERE id=?", (id,)).fetchone()
        return self._run_dict(row) if row else None

    def delete_run(self, id: str) -> bool:
        with self.conn() as db:
            cur = db.execute("DELETE FROM runs WHERE id=?", (id,))
            deleted = cur.rowcount > 0
        if deleted:
            self.audit("assessment_deleted", id)
        return deleted

    def purge_runs(self, older_than_days: int) -> int:
        """Explicit retention operation; no background auto-deletion."""
        from datetime import timedelta
        if not isinstance(older_than_days, int) or not 1 <= older_than_days <= 3650:
            raise ValueError("Retention must be between 1 and 3650 days")
        cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).isoformat(timespec="seconds")
        with self.conn() as db:
            cur = db.execute("DELETE FROM runs WHERE created_at < ?", (cutoff,))
            count = cur.rowcount
        self.audit("assessment_retention_purge", f"{count} records over {older_than_days} days")
        return count

    def audit(self, event: str, detail: str = "") -> None:
        if not event.isidentifier():
            raise ValueError("Invalid audit event")
        with self.conn() as db:
            db.execute("INSERT INTO audit (event,detail,created_at) VALUES (?,?,?)",
                       (event, str(detail)[:180], utcnow()))

    def audit_events(self, limit: int = 100) -> list[dict]:
        with self.conn() as db:
            rows = db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (min(500,max(1,limit)),)).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _run_dict(row):
        item = dict(row)
        data = item.pop("result_json")
        digest = item.get("result_sha256")
        item["integrity"] = "verified" if digest and hashlib.sha256(data.encode("utf-8")).hexdigest() == digest else "legacy_unverified" if not digest else "mismatch"
        item["result"] = json.loads(data)
        return item
