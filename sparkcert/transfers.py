"""Opt-in bounded file transfers over existing, trusted OpenSSH connections.

Remote helper is a fixed, reviewed Python snippet. User filenames are passed
base64-encoded as data, never interpolated into remote shell syntax. No password
or private-key material is transferred or stored. Remote destinations for uploads
are generated names in a dedicated home directory; no overwrite of source files.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from uuid import uuid4

from .ssh import SSHError, ssh_command, validate_relative_path

MAX_TRANSFER_BYTES = 16 * 1024 * 1024
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")

# This script will be sent to a remote authenticated Linux host as a constant.
# No user input is evaluated as code; paths are JSON-decoded from base64 argv.
_REMOTE_HELPER = r'''
import base64, json, os, pathlib, stat, sys
mode, arg = sys.argv[1], sys.argv[2]
val = json.loads(base64.b64decode(arg).decode('utf-8'))
home = pathlib.Path.home().resolve(strict=True)
limit = 16 * 1024 * 1024
if mode == 'download':
    relative = val['path']
    candidate = (home / relative).resolve(strict=True)
    if not candidate.is_relative_to(home) or not candidate.is_file():
        raise ValueError('File outside home or not a regular file')
    if candidate.stat().st_size > limit:
        raise ValueError('File exceeds the 16 MiB download limit')
    with open(candidate, 'rb') as f:
        buf = f.read(limit + 1)
    if len(buf) > limit:
        raise ValueError('File grew beyond download limit')
    sys.stdout.buffer.write(buf)
elif mode == 'upload':
    name = val['name']
    unique = val['unique']
    folder = home / 'sparkcert-uploads'
    if folder.is_symlink():
        raise ValueError('Uploads folder may not be a symlink')
    folder.mkdir(mode=0o700, exist_ok=True)
    if folder.resolve(strict=True).parent != home:
        raise ValueError('Uploads folder must be under home')
    os.chmod(folder, 0o700)
    target = folder / (unique + '_' + name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(str(target), flags, 0o600)
    try:
        with os.fdopen(fd, 'wb') as f:
            size = 0
            while True:
                part = sys.stdin.buffer.read(65536)
                if not part:
                    break
                size += len(part)
                if size > limit:
                    raise ValueError('Upload exceeds limit')
                f.write(part)
        print(json.dumps({'path': 'sparkcert-uploads/' + target.name, 'bytes': size}))
    except BaseException:
        target.unlink(missing_ok=True)
        raise
else:
    raise ValueError('Unknown operation')
'''


def clean_name(filename: str) -> str:
    if not NAME_RE.fullmatch(filename) or filename in (".", "..") or filename.startswith("."):
        raise SSHError("Use a filename of 1–100 ASCII letters, digits, dots, dashes or underscores")
    return filename


def _remote_transfer(device: dict, mode: str, payload: dict, content: bytes | None = None) -> bytes:
    if mode not in ("download", "upload"):
        raise SSHError("Invalid transfer mode")
    if content is not None and len(content) > MAX_TRANSFER_BYTES:
        raise SSHError("Uploads are limited to 16 MiB")
    arg = base64.b64encode(json.dumps(payload).encode()).decode()
    remote_command = "python3 -c " + shlex.quote(_REMOTE_HELPER) + " " + mode + " " + shlex.quote(arg)
    args = ssh_command(device)
    args[-2:-2] = ["-T"]
    try:
        proc = subprocess.run(args + [remote_command], input=content if content is not None else b"",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=75, check=False)
    except subprocess.TimeoutExpired as exc:
        raise SSHError("File transfer timed out") from exc
    except OSError as exc:
        raise SSHError(f"File transfer could not start: {exc}") from exc
    if proc.returncode:
        err = proc.stderr.decode("utf-8", errors="replace")[-500:]
        raise SSHError(("SSH file transfer failed: " + err).strip()[:520])
    if len(proc.stdout) > MAX_TRANSFER_BYTES + 512:
        raise SSHError("Transfer exceeded maximum allowed response size")
    return proc.stdout


def download_file(device: dict, relative_path: str) -> tuple[str, bytes]:
    relative = validate_relative_path(relative_path)
    if relative == ".":
        raise SSHError("Select a file, not a directory")
    blob = _remote_transfer(device, "download", {"path": relative})
    return Path(relative).name, blob


def upload_file(device: dict, name: str, content: bytes) -> dict:
    filename = clean_name(name)
    if len(content) > MAX_TRANSFER_BYTES:
        raise SSHError("Maximum supported file upload is 16 MiB")
    unique = uuid4().hex[:12]
    result = _remote_transfer(device, "upload", {"name": filename, "unique": unique}, content)
    try:
        parsed = json.loads(result)
        if not isinstance(parsed["bytes"], int) or parsed["bytes"] != len(content):
            raise ValueError("Transferred byte count mismatch")
        expected = f"sparkcert-uploads/{unique}_{filename}"
        if parsed["path"] != expected:
            raise ValueError("Remote upload path mismatch")
    except (ValueError, KeyError, TypeError) as exc:
        raise SSHError("Upload response did not pass integrity checks") from exc
    return parsed
