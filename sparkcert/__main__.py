"""Launch the local-only SparkCert UI."""
from __future__ import annotations

import argparse
import socket
import threading
import time
import webbrowser

import uvicorn


def find_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description="SparkCert — local AI readiness workbench")
    parser.add_argument("--port", type=int, default=0, help="Local port (default: random available port)")
    parser.add_argument("--no-browser", action="store_true", help="Do not launch browser")
    args = parser.parse_args()
    port = args.port or find_port()
    url = f"http://127.0.0.1:{port}/"
    if not args.no_browser:
        def launch():
            time.sleep(1)
            webbrowser.open(url)
        threading.Thread(target=launch, daemon=True).start()
    print(f"SparkCert running locally: {url}\nPress Ctrl+C to stop.", flush=True)
    uvicorn.run("sparkcert.app:app", host="127.0.0.1", port=port,
                log_level="warning", access_log=False)


if __name__ == "__main__":
    main()
