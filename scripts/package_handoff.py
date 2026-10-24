"""Generate portable SparkCert source ZIP; never package runtime credentials or local DB."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build", ".mypy_cache", ".ruff_cache", ".ssh", ".idea", ".vscode", "node_modules"}
EXCLUDE_FILENAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "known_hosts", "config", "sparkcert.db"}
EXCLUDE_SUFFIXES = {".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite3", ".pem", ".key", ".p12", ".pfx", ".pyc", ".log", ".zip", ".dmg", ".exe", ".app"}


def list_sources():
    result = []
    for file in ROOT.rglob("*"):
        if not file.is_file():
            continue
        rel = file.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if file.name in EXCLUDE_FILENAMES or file.name.startswith(".env"):
            continue
        if any(file.name.lower().endswith(ext) for ext in EXCLUDE_SUFFIXES):
            continue
        if file.is_symlink():
            continue
        result.append(file)
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description="Package safe SparkCert source handoff")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "SparkCert-v0.1.0-handoff-20261025.zip")
    args = parser.parse_args()
    target = args.output.resolve()
    if ROOT in target.parents or target == ROOT:
        raise SystemExit("Write archive outside the source directory to avoid accidentally packaging the archive")
    target.parent.mkdir(parents=True, exist_ok=True)
    files = list_sources()
    checksums = {str(f.relative_to(ROOT)).replace(os.sep, "/"): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    manifest = {
        "project": "SparkCert", "version": "0.1.0", "snapshot_date": "2026-10-25",
        "release_status": "local-first MVP; hardware/distribution/production unverified",
        "owner": "Md Najmul Hossain", "root_folder": "SparkCert",
        "source_files": checksums,
        "excluded_runtime_data": "SSH configs/keys, credentials, .env, databases, logs, virtualenvs, build output",
        "continuation_entry_point": "SparkCert/docs/WORKSPACE_HANDOFF.md"
    }
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for f in files:
            archive.write(f, arcname="SparkCert/" + str(f.relative_to(ROOT)).replace(os.sep, "/"))
        archive.writestr("SparkCert/SOURCE_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Archived {len(files)} source files: {target}")
    print(f"SHA256: {hashlib.sha256(target.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
