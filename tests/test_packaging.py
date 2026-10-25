"""Read-only sanity checks for the packaged desktop entry point."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import types

import desktop_launcher


def test_package_self_check_with_webview_importable(monkeypatch, tmp_path: Path):
    # CI package job runs the REAL packaged binary; this unit test mocks just
    # the optional webview import so it can run in a headless development env.
    monkeypatch.setitem(sys.modules, "webview", types.ModuleType("webview"))
    dest = tmp_path / "package-check.json"
    assert desktop_launcher.package_self_check(dest) == 0
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["checks"] == {
        "index.html": True, "styles.css": True,
        "app.js": True, "fastapi_routes": True
    }
    assert payload["scope"] == "packaging/import smoke only"


def test_package_self_check_fails_without_assets(monkeypatch, tmp_path: Path):
    import sparkcert.app as app_module
    monkeypatch.setitem(sys.modules, "webview", types.ModuleType("webview"))
    monkeypatch.setattr(app_module, "ASSETS", tmp_path / "missing")
    dest = tmp_path / "missing-check.json"
    assert desktop_launcher.package_self_check(dest) == 1
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert payload["checks"]["index.html"] is False
