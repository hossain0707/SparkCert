"""SSH over system OpenSSH: honors known_hosts, ssh-agent, ProxyJump, Include, etc."""
from __future__ import annotations

import ipaddress
import os
import re
import shutil
import subprocess
from pathlib import Path

HOST_PATTERN = re.compile(r"^[A-Za-z0-9_.:\-]+$")
USER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*[$]?$|^[A-Za-z0-9_][A-Za-z0-9_.-]*$")
# We do not allow ssh user-controlled -o options. Hostname and alias are treated as operands,
# never parsed as command-line flags.


class SSHError(Exception):
    pass


def verify_host(host: str) -> str:
    host = host.strip()
    if not host or len(host) > 253 or not HOST_PATTERN.fullmatch(host) or host.startswith("-"):
        raise SSHError("Invalid SSH hostname or alias")
    return host


def config_aliases(path: Path | None = None) -> list[dict]:
    """Read named Host entries from SSH config. 'Include' supports user-owned snippets."""
    base = path or Path.home() / ".ssh" / "config"
    seen = set()
    aliases: list[dict] = []

    def visit(file: Path, depth: int = 0):
        if depth >= 5 or file in seen or not file.is_file():
            return
        seen.add(file)
        try:
            if file.stat().st_size > 1024 * 1024:
                return
            contents = file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        for line in contents.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            command, value = parts[0].lower(), parts[1].strip().strip('"')
            if command == "host":
                for alias in value.split():
                    if ("*" not in alias and "?" not in alias and "!" not in alias
                            and HOST_PATTERN.fullmatch(alias) and not alias.startswith("-")):
                        aliases.append({"alias": alias})
            elif command == "include":
                # Includes can be absolute or relative to ~/.ssh, per OpenSSH convention.
                import glob
                for pattern in value.split():
                    candidate = Path(pattern).expanduser()
                    if not candidate.is_absolute():
                        candidate = Path.home() / ".ssh" / candidate
                    for match in glob.glob(str(candidate))[:40]:
                        visit(Path(match), depth + 1)

    visit(base)
    return sorted({a["alias"]: a for a in aliases}.values(), key=lambda x: x["alias"].lower())


def ssh_command(device: dict, *, batch_mode: bool = True) -> list[str]:
    if not shutil.which("ssh"):
        raise SSHError("OpenSSH client not found. Install OpenSSH Client first.")
    alias = device.get("ssh_alias", "").strip()
    host = verify_host(alias or device.get("host", ""))
    command = ["ssh", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=8",
               "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=10",
               "-o", "ServerAliveCountMax=1"]
    if batch_mode:
        command += ["-o", "BatchMode=yes"]
    if not alias:
        port = int(device.get("port", 22))
        if not 1 <= port <= 65535:
            raise SSHError("Invalid SSH port")
        command.extend(["-p", str(port)])
        username = device.get("username", "").strip()
        if username:
            if not USER_PATTERN.fullmatch(username):
                raise SSHError("Invalid SSH username")
            command.extend(["-l", username])
        identity = device.get("identity_file", "").strip()
        if identity:
            full = Path(identity).expanduser()
            if not full.is_file():
                raise SSHError("SSH private key file not found")
            command.extend(["-i", str(full)])
    command += ["--", host]
    return command


def _ssh_run(device: dict, script: str, timeout: int = 25) -> str:
    command = ssh_command(device)
    try:
        proc = subprocess.run(command + ["sh", "-s"], input=script, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=timeout, check=False, stdin=None)
    except subprocess.TimeoutExpired as exc:
        raise SSHError("SSH timed out. Check the network/VPN and device status.") from exc
    except OSError as exc:
        raise SSHError(f"SSH could not start: {exc}") from exc
    if proc.returncode != 0:
        error = proc.stderr.strip()[-700:]
        if "Host key verification failed" in error:
            raise SSHError("Host key verification failed. Confirm this device's SSH fingerprint in a trusted terminal.")
        if "Permission denied" in error:
            raise SSHError("Authentication failed. Configure an SSH key or unlock your SSH agent.")
        raise SSHError(error or f"SSH returned exit status {proc.returncode}")
    return proc.stdout[:120000]


# Must not interpolate any remote-supplied input into the shell script.
HEALTH_SCRIPT = r'''
printf 'SC_HOST='; hostname 2>/dev/null || true
printf 'SC_OS='; uname -s 2>/dev/null || true
printf 'SC_ARCH='; uname -m 2>/dev/null || true
printf 'SC_UPTIME='; uptime -p 2>/dev/null || true
printf 'SC_MEMORY_KB='; awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo 2>/dev/null || true
printf 'SC_MEMORY_AVAILABLE_KB='; awk '/^MemAvailable:/ {print $2; exit}' /proc/meminfo 2>/dev/null || true
printf 'SC_DISK='; df -Pk "$HOME" 2>/dev/null | awk 'NR==2 {print $2 "," $3 "," $4}' || true
printf 'SC_GPU='; nvidia-smi --query-gpu=name,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits 2>/dev/null | head -n 4 || true
printf 'SC_CUDA='; nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n 1 || true
printf 'SC_DOCKER='; (command -v docker >/dev/null 2>&1 && docker info --format '{{.ServerVersion}}' 2>/dev/null) || true
printf 'SC_PYTHON='; python3 --version 2>&1 || true
printf 'SC_END=1\n'
'''


def health_probe(device: dict) -> dict:
    raw = _ssh_run(device, HEALTH_SCRIPT, timeout=28)
    parsed = {}
    for line in raw.splitlines():
        if line.startswith("SC_") and "=" in line:
            key, value = line[3:].split("=", 1)
            parsed[key.lower()] = value.strip()
    if parsed.get("end") != "1":
        raise SSHError("Incomplete diagnostics response from remote device")
    mem_total = int(parsed.get("memory_kb") or 0)
    mem_available = int(parsed.get("memory_available_kb") or 0)
    disk = parsed.get("disk", "").split(",")
    gpu = parsed.get("gpu", "")
    gpu_fields = [v.strip() for v in gpu.split(",")] if gpu else []
    return {
        "hostname": parsed.get("host", "Unknown"), "os": parsed.get("os", "Unknown"),
        "architecture": parsed.get("arch", "Unknown"), "uptime": parsed.get("uptime") or "Unavailable",
        "memory_gb": round(mem_total / 1048576, 1) if mem_total else None,
        "memory_used_pct": round(100 * (1 - mem_available / mem_total), 1) if mem_total else None,
        "disk_total_gb": round(int(disk[0]) / 1048576, 1) if len(disk) == 3 and disk[0].isdigit() else None,
        "disk_used_pct": round(int(disk[1]) / int(disk[0]) * 100, 1) if len(disk) == 3 and disk[0].isdigit() and int(disk[0]) else None,
        "gpu_name": gpu_fields[0] if gpu_fields else None,
        "gpu_util_pct": _number(gpu_fields[1]) if len(gpu_fields) > 1 else None,
        "gpu_temp_c": _number(gpu_fields[2]) if len(gpu_fields) > 2 else None,
        "gpu_power_w": _number(gpu_fields[3]) if len(gpu_fields) > 3 else None,
        "nvidia_driver": parsed.get("cuda") or None,
        "docker_version": parsed.get("docker") or None,
        "python_version": parsed.get("python") or None,
        "raw": parsed,
    }


def _number(raw):
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def readiness_probe(device: dict) -> dict:
    """Evidenced host-level prerequisites, not an official certification."""
    health = health_probe(device)
    checks = [
        {"id": "ssh", "name": "Authenticated SSH connectivity", "passed": True,
         "detail": "Successfully reached host with verified SSH host key."},
        {"id": "linux", "name": "Linux environment", "passed": health["os"] == "Linux",
         "detail": f"Detected OS: {health['os']}"},
        {"id": "gpu", "name": "NVIDIA GPU visibility", "passed": bool(health["gpu_name"]),
         "detail": health["gpu_name"] or "nvidia-smi GPU data unavailable"},
        {"id": "memory", "name": "Memory headroom (20% minimum)",
         "passed": health["memory_used_pct"] is not None and health["memory_used_pct"] <= 80,
         "detail": f"Memory used: {health['memory_used_pct']}%" if health["memory_used_pct"] is not None else "Memory statistics unavailable"},
        {"id": "storage", "name": "Storage headroom (15% minimum)",
         "passed": health["disk_used_pct"] is not None and health["disk_used_pct"] <= 85,
         "detail": f"Disk used: {health['disk_used_pct']}%" if health["disk_used_pct"] is not None else "Disk statistics unavailable"},
        {"id": "python", "name": "Python 3 installed", "passed": "Python 3" in (health["python_version"] or ""),
         "detail": health["python_version"] or "Python unavailable"},
        {"id": "docker", "name": "Docker daemon accessible", "passed": bool(health["docker_version"]),
         "detail": health["docker_version"] or "Docker unavailable or permission denied"},
    ]
    count = sum(x["passed"] for x in checks)
    score = round(count * 100 / len(checks))
    return {"status": "completed", "score": score, "checks": checks, "health": health,
            "summary": f"{count}/{len(checks)} infrastructure checks passed",
            "scope": "Infrastructure prerequisites only. Not a complete application certification.",
            "method": "Remote read-only diagnostics over OpenSSH"}


def open_terminal(device: dict) -> str:
    """Open the user's own terminal for an interactive SSH session.

    System terminal performs password prompts; we neither capture nor store them.
    """
    import sys
    import shlex
    import tempfile
    cmd = ssh_command(device, batch_mode=False)
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.Popen(cmd, creationflags=flags, close_fds=True)
        return "Opened OpenSSH in a new Windows console"
    if sys.platform == "darwin":
        folder = Path.home() / ".sparkcert" / "terminal"
        folder.mkdir(parents=True, exist_ok=True)
        folder.chmod(0o700)
        script = folder / "connect.command"
        # This executable is only accessed by the current OS user; do not put secrets in it.
        script.write_text("#!/bin/sh\n" + shlex.join(cmd) + "\n", encoding="utf-8")
        script.chmod(0o700)
        subprocess.Popen(["open", "-a", "Terminal", str(script)], close_fds=True)
        return "Opened OpenSSH in macOS Terminal"
    terminals = [
        ["x-terminal-emulator", "-e", *cmd],
        ["gnome-terminal", "--", *cmd],
        ["konsole", "-e", *cmd],
        ["xfce4-terminal", "-x", *cmd],
        ["xterm", "-e", *cmd],
    ]
    for candidate in terminals:
        if shutil.which(candidate[0]):
            subprocess.Popen(candidate, close_fds=True)
            return "Opened OpenSSH in desktop terminal"
    raise SSHError("No supported desktop terminal found. Copy the SSH command and run it in your terminal.")


def validate_relative_path(raw: str) -> str:
    """Restrict file browsing to clean home-relative paths; block traversal."""
    import posixpath
    raw = raw.strip()
    if len(raw) > 400 or raw.startswith(('/', '-', '~')) or any(c in raw for c in ('\\', ':', '\x00', '\n', '\r')):
        raise SSHError("Invalid relative path")
    sections = raw.split('/')
    if any(part in ('..', '') for part in sections):
        raise SSHError("Parent traversal and empty path segments are not permitted")
    return raw or '.'


def list_remote_files(device: dict, path: str = '.') -> list[dict]:
    import shlex
    safe = validate_relative_path(path)
    # Directory must resolve within the account's home, including symbolic links.
    quote = shlex.quote(safe)
    script = f'''set -eu
root=$(realpath -e "$HOME")
target=$(realpath -e "$HOME"/{quote})
case "$target" in "$root"|"$root"/*) ;; *) echo 'SC_ERROR=outside_home'; exit 1;; esac
[ -d "$target" ] || {{ echo 'SC_ERROR=not_directory'; exit 1; }}
find "$target" -mindepth 1 -maxdepth 1 -printf '%y\\t%f\\t%s\\n' 2>/dev/null | head -n 300
'''
    output = _ssh_run(device, script, 25)
    files=[]
    for line in output.splitlines():
        parts = line.split('\t',2)
        if len(parts)==3:
            type_,name,size=parts
            if name in ('..','.') or any(c in name for c in ('\x00','\r','\n','/')):continue
            files.append({"name":name, "type":"directory" if type_=='d' else "file" if type_=='f' else "link", "size":int(size) if size.isdigit() else None})
    return sorted(files, key=lambda f: (f['type']!='directory',f['name'].lower()))
