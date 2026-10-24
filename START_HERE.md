# Continue SparkCert development

**Project:** [hossain0707/SparkCert](https://github.com/hossain0707/SparkCert) · **Owner:** Md Najmul Hossain · **Current state:** v0.1.0 development MVP.

This file is the short entry point for a new machine, ChatGPT workspace, Codex agent, or collaborator. **Do not restart or rewrite from a blank project.** The repository includes an executable MVP, not a release-verified commercial application.

## Read in this order

1. [Repository agent instructions](AGENTS.md)
2. [Canonical handover](docs/WORKSPACE_HANDOFF.md)
3. [Completed and incomplete feature matrix](docs/PROJECT_STATUS.md)
4. [System architecture](docs/ARCHITECTURE.md) and [animated architecture](docs/ARCHITECTURE.html)
5. [UI design and motion specification](docs/DESIGN_SYSTEM.md)
6. [Verification evidence and hardware matrix](docs/VERIFICATION.md)
7. [Development roadmap](docs/PRODUCT_ROADMAP.md)
8. [Reusable prompt for a new workspace](docs/CONTINUE_IN_NEW_WORKSPACE.md)

## First command sequence

```bash
python -m venv .venv
# activate your venv (Windows: .venv\\Scripts\\Activate.ps1; macOS/Linux: source .venv/bin/activate)
python -m pip install -e '.[dev]'
python -m pytest -q
node --check web/app.js
python -m sparkcert
```

## What is already real

Local-first browser/optional pywebview workbench, OpenSSH profiles/aliases, key/agent/strict host-key transport, read-only diagnostics, limited real HTTP model checks, SQLite evidence records and PDF exports. It is a working codebase, **but not verified on an actual DGX Spark or clean signed installer release**.

## Next milestone

First validate SSH connectivity on physical DGX Spark from Windows/macOS/Linux over direct Ethernet, LAN and private VPN; document each configuration, negative test and measured outcome. Then fix cross-platform packaging and prioritize secure guided onboarding. See `docs/PROJECT_STATUS.md` for exact acceptance gates.
