"""Explicit, loopback-only SSH port forwarding for privately hosted model APIs.

No SSH key material is handled here. System OpenSSH enforces known_hosts.
Tunnels are ephemeral subprocesses, never stored as reconnect credentials.
"""
from __future__ import annotations

import atexit
import os
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from uuid import uuid4

from .ssh import SSHError, ssh_command


@dataclass
class Forward:
    id: str
    device_id: str
    device_name: str
    local_port: int
    remote_port: int
    process: subprocess.Popen
    started_at: float


class TunnelManager:
    """Per-process tunnel registry, with explicit lifetime and bounded capacity."""

    def __init__(self, max_tunnels: int = 4):
        self.max_tunnels = max_tunnels
        self._tunnels: dict[str, Forward] = {}
        self._lock = threading.RLock()
        atexit.register(self.close_all)

    @staticmethod
    def _free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def list(self) -> list[dict]:
        with self._lock:
            for id, item in list(self._tunnels.items()):
                if item.process.poll() is not None:
                    del self._tunnels[id]
            return [self._present(item) for item in self._tunnels.values()]

    @staticmethod
    def _present(item: Forward) -> dict:
        return {"id": item.id, "device_id": item.device_id, "device_name": item.device_name,
                "local_port": item.local_port, "remote_port": item.remote_port,
                "endpoint": f"http://127.0.0.1:{item.local_port}/v1",
                "status": "ssh_forward_active", "started_at_unix": round(item.started_at)}

    def start(self, device: dict, remote_port: int, local_port: int = 0) -> dict:
        if not isinstance(remote_port, int) or not 1 <= remote_port <= 65535:
            raise SSHError("Remote port must be between 1 and 65535")
        if not isinstance(local_port, int) or not 0 <= local_port <= 65535:
            raise SSHError("Local port must be 0 (automatic) or 1–65535")
        with self._lock:
            self.list()
            if len(self._tunnels) >= self.max_tunnels:
                raise SSHError("Maximum active SSH tunnels reached")
            port = local_port or self._free_port()
            args = ssh_command(device, batch_mode=True)
            # OpenSSH's -L and -N options MUST precede `-- host`.
            args[-2:-2] = ["-o", "ExitOnForwardFailure=yes", "-o", "ClearAllForwardings=yes",
                             "-o", "ControlMaster=no", "-N", "-T",
                             "-L", f"127.0.0.1:{port}:127.0.0.1:{remote_port}"]
            try:
                proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.PIPE, close_fds=True)
            except OSError as exc:
                raise SSHError(f"Unable to start SSH port forwarding: {exc}") from exc
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                code = proc.poll()
                if code is not None:
                    detail = (proc.stderr.read(600) if proc.stderr else b"").decode(errors="replace").strip()
                    raise SSHError((detail or f"SSH exited with status {code}")[:350])
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                        break
                except (TimeoutError, OSError):
                    time.sleep(0.1)
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                raise SSHError("SSH tunnel did not become reachable; verify SSH access and port availability")
            forward = Forward(str(uuid4()), device["id"], device["name"], port,
                              remote_port, proc, time.time())
            self._tunnels[forward.id] = forward
            return self._present(forward)

    def stop(self, id: str) -> bool:
        with self._lock:
            forward = self._tunnels.pop(id, None)
            if not forward:
                return False
            if forward.process.poll() is None:
                forward.process.terminate()
                try:
                    forward.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    forward.process.kill()
                    forward.process.wait(timeout=2)
            if forward.process.stderr:
                forward.process.stderr.close()
            return True

    def stop_for_device(self, device_id: str) -> None:
        with self._lock:
            for id, forward in list(self._tunnels.items()):
                if forward.device_id == device_id:
                    self.stop(id)

    def close_all(self) -> None:
        with self._lock:
            for id in list(self._tunnels):
                self.stop(id)
