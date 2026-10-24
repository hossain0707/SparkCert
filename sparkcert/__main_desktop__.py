"""Optional native window entry point; requires pip install sparkcert[desktop]."""
import socket
import threading
import time
import uvicorn

from .app import app


def main():
    import webview
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
                                           log_level="warning", access_log=False))
    threading.Thread(target=server.run, daemon=True).start()
    webview.create_window("SparkCert — AI Readiness Workbench", f"http://127.0.0.1:{port}",
                          min_size=(1080, 720), width=1440, height=900)
    try:
        webview.start()
    finally:
        server.should_exit = True


if __name__ == "__main__":
    main()
