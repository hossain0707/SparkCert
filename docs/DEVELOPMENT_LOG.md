# SparkCert development log

## 2026-10-25 — local-first v0.1.0 development snapshot

- Completed local Python/FastAPI + responsive UI prototype, OpenSSH host profile import, read-only remote diagnostics, limited OpenAI-compatible model evaluation and PDF evidence export.
- Executed local `python -m pytest -q`: **9 passed** in development container (Python 3.13, pytest 9.0.2). No DGX Spark physical hardware connection evidenced.
- Added cross-workspace technical handover, architecture diagrams and a motion/accessibility design specification.
- Added reduced-motion-aware subtle UI transitions; further browser usability, screen-reader and performance validation outstanding.
- Outstanding highest priority: real Windows/macOS/Linux installer validation, real Ethernet/LAN/VPN Spark connection matrix, target identity and secure endpoint onboarding, release signing, security review.

When continuing, append date, GitHub commit, tests executed, OS/DGX Spark version, evidence paths, unresolved issues and next tasks. Avoid converting planned capabilities into completed claims.

## 2026-10-25 — v0.2.0 feature development

- `sparkcert/tunnels.py`: explicit opt-in private SSH forwards, 4-tunnel cap, strict host verification delegated to OpenSSH, lifecycle cleanup.
- `sparkcert/transfers.py`: limited remote Python3 home-directory file download; unique 0700 remote upload directory, max 16 MiB, no overwrite, explicit client consent.
- `sparkcert/evaluation.py`: 1–3 repeat runs and 1–4 request concurrency, measured p50/p95 and model response size cap.
- `sparkcert/store.py`: SQLite digest migration, local non-prompt audit trail, retention/delete.
- `sparkcert/app.py`: new authenticated tunnel/file/report/audit endpoints.
- `sparkcert/reports.py`: evidence digest and measured timing displayed in PDF; checksum mismatch blocks PDF exports.
- `web/app.js`, `web/styles.css`: animated/responsive private tunnel, file upload/download, retention and audit UI; new evaluation controls.
- `.github/workflows/ci.yml`: multi-OS Python test and build candidates, security audit/SBOM job; workflow itself not remotely verified.
- `tests/test_v02.py`, `scripts/ui_smoke.py`: six new automated tests and an offline Chromium UI smoke test (mock-only).
- No physical hardware connection, production signing, external audit or release publication.
