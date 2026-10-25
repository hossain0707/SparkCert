"""v0.2 regression and security boundaries; no claims of physical-hardware coverage."""
import hashlib
import io
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from sparkcert.app import create_app
from sparkcert.evaluation import DEFAULT_CASES, evaluate
from sparkcert.ssh import SSHError
from sparkcert.store import Store
from sparkcert.transfers import MAX_TRANSFER_BYTES, clean_name, download_file, upload_file
from sparkcert.tunnels import TunnelManager


@pytest.fixture()
def session(tmp_path):
    app = create_app(Store(tmp_path))
    with TestClient(app) as client:
        yield client, app, {"X-SparkCert-Token": app.state.token}
    app.state.tunnels.close_all()


def test_reports_integrity_delete_and_audit(session):
    client, app, headers = session
    record = app.state.store.add_run("model_behavior", {"status": "completed", "score": 100,
                                                          "summary": "actual result", "cases": []})
    assert record["integrity"] == "verified"
    assert client.get("/api/audit", headers=headers).json()[0]["event"] == "assessment_saved"
    assert client.get(f"/api/reports/{record['id']}/pdf", headers=headers).content.startswith(b"%PDF")
    with sqlite3.connect(app.state.store.path) as db:
        db.execute("UPDATE runs SET result_json=? WHERE id=?", ('{"score": 0}', record["id"]))
    assert client.get(f"/api/reports/{record['id']}", headers=headers).json()["integrity"] == "mismatch"
    assert client.get(f"/api/reports/{record['id']}/pdf", headers=headers).status_code == 409
    assert client.delete(f"/api/reports/{record['id']}").status_code == 401
    assert client.delete(f"/api/reports/{record['id']}", headers=headers).status_code == 200
    assert client.get(f"/api/reports/{record['id']}", headers=headers).status_code == 404


def test_explicit_retention(session):
    client, app, headers = session
    store = app.state.store
    old = store.add_run("infrastructure", {"score": 100})
    fresh = store.add_run("infrastructure", {"score": 80})
    old_time = (datetime.now(timezone.utc) - timedelta(days=200)).isoformat(timespec="seconds")
    with sqlite3.connect(store.path) as db:
        db.execute("UPDATE runs SET created_at=? WHERE id=?", (old_time, old["id"]))
    assert client.post("/api/reports/retention", json={"older_than_days": 90}).status_code == 401
    assert client.post("/api/reports/retention", headers=headers,
                       json={"older_than_days": 0}).status_code == 422
    answer = client.post("/api/reports/retention", headers=headers,
                         json={"older_than_days": 90}).json()
    assert answer["deleted"] == 1
    assert store.run(old["id"]) is None and store.run(fresh["id"]) is not None


def test_tunnel_lifecycle_with_mocked_ssh_and_socket(monkeypatch):
    class FakeProcess:
        stderr = io.BytesIO(b"")
        def __init__(self):
            self.alive = True
        def poll(self):
            return None if self.alive else 0
        def terminate(self):
            self.alive = False
        def kill(self):
            self.alive = False
        def wait(self, timeout=None):
            return 0

    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None

    commands = []
    def popen(args, **kwargs):
        commands.append(args)
        return FakeProcess()

    monkeypatch.setattr("sparkcert.tunnels.ssh_command", lambda device, batch_mode=True: ["ssh", "--", "spark"])
    monkeypatch.setattr("sparkcert.tunnels.subprocess.Popen", popen)
    monkeypatch.setattr("sparkcert.tunnels.socket.create_connection", lambda *a, **kw: Connection())
    monkeypatch.setattr(TunnelManager, "_free_port", staticmethod(lambda: 54321))
    manager = TunnelManager(max_tunnels=1)
    dev = {"id": "dev-1", "name": "DGX Lab"}
    active = manager.start(dev, remote_port=8000)
    assert active["endpoint"] == "http://127.0.0.1:54321/v1"
    assert "127.0.0.1:54321:127.0.0.1:8000" in commands[0]
    assert "ExitOnForwardFailure=yes" in commands[0]
    with pytest.raises(SSHError, match="Maximum"):
        manager.start(dev, 8000)
    assert manager.stop(active["id"])
    assert manager.list() == []
    assert not manager.stop(active["id"])
    with pytest.raises(SSHError):
        manager.start(dev, 0)


def test_tunnel_api_authorization_and_cleanup(session):
    client, app, headers = session
    with patch("sparkcert.app.ssh_command", return_value=["ssh", "--", "spark"]):
        device = client.post("/api/devices", headers=headers, json={"name": "Spark", "host": "spark.local"}).json()
    assert client.get("/api/tunnels").status_code == 401
    assert client.get("/api/tunnels", headers=headers).json() == []
    assert client.post("/api/tunnels", headers=headers, json={"device_id": device["id"], "remote_port": 0}).status_code == 422
    fake = {"id": "tunnel-1", "device_id": device["id"], "device_name": "Spark",
            "local_port": 48000, "remote_port": 8000, "endpoint": "http://127.0.0.1:48000/v1"}
    with patch.object(app.state.tunnels, "start", return_value=fake), patch.object(app.state.tunnels, "stop", return_value=True):
        r = client.post("/api/tunnels", headers=headers, json={"device_id": device["id"], "remote_port": 8000})
        assert r.status_code == 201
        assert client.delete("/api/tunnels/tunnel-1", headers=headers).status_code == 200


def test_transfers_limit_paths_and_upload_response(session, monkeypatch):
    client, app, headers = session
    for name in ("../../oops", "name with spaces", ".ssh", "-danger", "\na", "A" * 110):
        with pytest.raises(SSHError):
            clean_name(name)
    assert clean_name("report-2026.csv") == "report-2026.csv"
    with pytest.raises(SSHError):
        upload_file({"host": "spark"}, "abc.txt", b"x" * (MAX_TRANSFER_BYTES + 1))
    monkeypatch.setattr("sparkcert.transfers._remote_transfer", lambda device, mode, payload, content=None:
                        json.dumps({"path": f"sparkcert-uploads/{payload['unique']}_{payload['name']}",
                                    "bytes": len(content or b"")}).encode() if mode == "upload" else b"file-data")
    saved = upload_file({"host": "spark"}, "report.txt", b"hello")
    assert saved["bytes"] == 5 and saved["path"].startswith("sparkcert-uploads/")
    name, blob = download_file({"host": "spark"}, "reports/summary.txt")
    assert (name, blob) == ("summary.txt", b"file-data")
    with pytest.raises(SSHError):
        download_file({"host": "spark"}, "../../etc/shadow")
    with patch("sparkcert.app.ssh_command", return_value=["ssh", "--", "spark"]):
        dev = client.post("/api/devices", headers=headers, json={"name": "Spark", "host": "spark.local"}).json()
    with patch("sparkcert.app.upload_file", return_value={"path": "sparkcert-uploads/sample.txt", "bytes": 4}):
        response = client.post(f"/api/devices/{dev['id']}/upload", headers=headers,
                               files={"upload": ("sample.txt", b"abcd")})
        assert response.status_code == 200
    with patch("sparkcert.app.download_file", return_value=("sample.txt", b"test-data")):
        response = client.get(f"/api/devices/{dev['id']}/download?path=sample.txt", headers=headers)
        assert response.content == b"test-data"
        assert response.headers["content-type"] == "application/octet-stream"


def test_repeated_parallel_evaluation_with_mock_transport():
    def mock(req):
        return httpx.Response(200, json={"choices": [{"message": {"content": "SPARKCERT_READY"}}],
                                         "usage": {"total_tokens": 11}})
    real_client = httpx.Client
    class FakeClient(real_client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, transport=httpx.MockTransport(mock), **kwargs)
    with patch("sparkcert.evaluation.httpx.Client", FakeClient):
        result = evaluate("http://127.0.0.1:8000/v1", "model", [DEFAULT_CASES[0]],
                          repetitions=3, concurrency=2)
    assert result["requests_total"] == 3
    assert result["requests_without_transport_errors"] == 3
    assert result["latency_p50_ms"] is not None
    assert result["cases"][0]["sample_count"] == 3
    assert result["score"] == 100
