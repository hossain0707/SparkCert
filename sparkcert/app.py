"""Local-only SparkCert HTTP API. Never expose this server on a public interface."""
from __future__ import annotations

import asyncio
import html
import os
import secrets
import shutil
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from . import __version__
from .evaluation import DEFAULT_CASES, EvaluationError, evaluate
from .reports import pdf_bytes
from .ssh import SSHError, config_aliases, health_probe, readiness_probe, ssh_command, verify_host, open_terminal, list_remote_files, validate_relative_path
from .store import Store

ASSETS = Path(__file__).resolve().parent.parent / "web"


class DeviceIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    host: str = Field(default="", max_length=253)
    username: str = Field(default="", max_length=90)
    port: int = Field(default=22, ge=1, le=65535)
    ssh_alias: str = Field(default="", max_length=253)
    identity_file: str = Field(default="", max_length=550)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v):
        return v.strip()

    @field_validator("ssh_alias", "host")
    @classmethod
    def validate_host(cls, v):
        return verify_host(v) if v.strip() else ""

    @field_validator("identity_file")
    @classmethod
    def sanitize_identity(cls, v):
        v = v.strip()
        if "\x00" in v or "\n" in v or "\r" in v:
            raise ValueError("Invalid SSH identity file")
        return v


class CaseIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="Custom", max_length=100)
    system: str = Field(default="", max_length=4000)
    prompt: str = Field(min_length=1, max_length=5000)
    expected: str = Field(default="", max_length=2000)
    rule: Literal["exact", "contains", "not_contains", "json_key_value"] = "exact"


class EvaluateIn(BaseModel):
    endpoint: str = Field(min_length=7, max_length=500)
    model: str = Field(min_length=1, max_length=180)
    api_key: str = Field(default="", max_length=1000)
    cases: list[CaseIn] = Field(min_length=1, max_length=25)


class TestDevice(BaseModel):
    host: str = ""
    username: str = ""
    port: int = 22
    ssh_alias: str = ""
    identity_file: str = ""


def create_app(store: Store | None = None) -> FastAPI:
    app = FastAPI(title="SparkCert", version=__version__, docs_url=None, redoc_url=None,
                  openapi_url=None)
    app.state.store = store or Store()
    app.state.token = secrets.token_urlsafe(32)

    @app.middleware("http")
    async def security(request: Request, call_next):
        # Defense in depth; Uvicorn must also bind 127.0.0.1 only.
        host = request.url.hostname
        if host not in {"127.0.0.1", "localhost", "::1", "testserver"}:
            return Response("Local access only", status_code=403)
        origin = request.headers.get("origin")
        if origin:
            from urllib.parse import urlparse
            src = urlparse(origin)
            if src.hostname not in {"127.0.0.1", "localhost", "::1", "testserver"}:
                return Response("Invalid request origin", status_code=403)
        if request.url.path.startswith("/api/") and request.url.path not in {"/api/health"}:
            if not secrets.compare_digest(request.headers.get("x-sparkcert-token", ""), app.state.token):
                return Response("Unauthorized", status_code=401)
        result = await call_next(request)
        result.headers["X-Content-Type-Options"] = "nosniff"
        result.headers["X-Frame-Options"] = "DENY"
        result.headers["Referrer-Policy"] = "no-referrer"
        result.headers["Cache-Control"] = "no-store"
        result.headers["Content-Security-Policy"] = "default-src 'none'; connect-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'"
        return result

    @app.get("/", response_class=HTMLResponse)
    async def index():
        content = (ASSETS / "index.html").read_text(encoding="utf-8")
        return HTMLResponse(content.replace("__SPARKCERT_TOKEN__", html.escape(app.state.token, quote=True)))

    @app.get("/api/health")
    async def api_health():
        return {"ok": True, "version": __version__}

    @app.get("/api/overview")
    async def overview():
        devices = app.state.store.devices()
        runs = app.state.store.runs(limit=10)
        return {"version": __version__, "platform": os.name,
                "ssh_available": bool(shutil.which("ssh")),
                "device_count": len(devices), "run_count": len(app.state.store.runs()),
                "devices": devices, "recent_runs": runs}

    @app.get("/api/ssh/aliases")
    async def aliases():
        return {"aliases": config_aliases()}

    @app.get("/api/devices")
    async def devices():
        return app.state.store.devices()

    @app.post("/api/devices", status_code=201)
    async def add_device(payload: DeviceIn):
        if not payload.host and not payload.ssh_alias:
            raise HTTPException(422, "Host or SSH alias required")
        if not payload.name.strip():
            raise HTTPException(422, "Device name is required")
        try:
            ssh_command(payload.model_dump())
        except SSHError as exc:
            raise HTTPException(422, str(exc)) from exc
        return app.state.store.add_device(payload.model_dump())

    @app.delete("/api/devices/{id}")
    async def remove_device(id: str):
        if not app.state.store.delete_device(id):
            raise HTTPException(404, "Device not found")
        return {"ok": True}

    def require_device(id: str) -> dict:
        device = app.state.store.device(id)
        if not device:
            raise HTTPException(404, "Device not found")
        return device

    @app.post("/api/devices/{id}/probe")
    async def probe_device(id: str):
        dev = require_device(id)
        try:
            result = await asyncio.to_thread(health_probe, dev)
        except SSHError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"device": dev, "health": result, "connected": True}

    @app.post("/api/devices/{id}/terminal")
    async def terminal(id: str):
        dev = require_device(id)
        try:
            message = await asyncio.to_thread(open_terminal, dev)
        except (SSHError, OSError) as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"ok": True, "message": message}

    @app.get("/api/devices/{id}/files")
    async def files(id: str, path: str = "."):
        dev = require_device(id)
        try:
            files = await asyncio.to_thread(list_remote_files, dev, path)
        except SSHError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"path": validate_relative_path(path), "files": files}

    @app.post("/api/devices/{id}/readiness")
    async def readiness(id: str):
        dev = require_device(id)
        try:
            result = await asyncio.to_thread(readiness_probe, dev)
        except SSHError as exc:
            raise HTTPException(422, str(exc)) from exc
        run = app.state.store.add_run("infrastructure", result, id, dev["name"])
        return run

    @app.get("/api/evaluation/cases")
    async def default_cases():
        return DEFAULT_CASES

    @app.post("/api/evaluation/run")
    async def evaluate_model(payload: EvaluateIn):
        try:
            result = await asyncio.to_thread(evaluate, payload.endpoint, payload.model,
                                             [c.model_dump() for c in payload.cases], payload.api_key)
        except EvaluationError as exc:
            raise HTTPException(422, str(exc)) from exc
        # The caller's API token and remote model response headers are not persisted.
        return app.state.store.add_run("model_behavior", result, device_name=payload.model)

    @app.get("/api/reports")
    async def reports():
        return app.state.store.runs()

    @app.get("/api/reports/{id}")
    async def report(id: str):
        run = app.state.store.run(id)
        if not run:
            raise HTTPException(404, "Report not found")
        return run

    @app.get("/api/reports/{id}/pdf")
    async def report_pdf(id: str):
        run = app.state.store.run(id)
        if not run:
            raise HTTPException(404, "Report not found")
        content = await asyncio.to_thread(pdf_bytes, run)
        return Response(content, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="sparkcert-{id[:8]}.pdf"'})

    app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")
    return app


app = create_app()
