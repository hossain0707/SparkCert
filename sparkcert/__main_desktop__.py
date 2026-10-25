"""Native desktop window for SparkCert.

The HTTP control plane is strictly bound to loopback. The listener socket remains
reserved until Uvicorn takes ownership, preventing startup port races.
"""
from __future__ import annotations

import socket
import threading
import time

import uvicorn

from .app import app


def main() -> None:
    import webview

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port,
                       log_level="warning", access_log=False)
    )
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()
    try:
        # Don't open a blank/broken window while Uvicorn is still starting.
        for _ in range(100):
            if server.started:
                break
            if not thread.is_alive():
                raise RuntimeError("SparkCert local server stopped unexpectedly during startup")
            time.sleep(0.1)
        else:
            raise RuntimeError("SparkCert local server did not become ready")

        webview.create_window(
            "SparkCert — Private AI Readiness",
            f"http://127.0.0.1:{port}/",
            width=1360, height=860, min_size=(940, 620)
        )
        webview.start()
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()


if __name__ == "__main__":
    main()
