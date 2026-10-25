> **Current project: v0.2.0 development candidate, NOT production validated.** See `docs/PROJECT_STATUS.md`, `docs/VERIFICATION.md`, `docs/WORKSPACE_HANDOFF.md` and `CHANGELOG.md` for new tunnel, file transfer, evaluation and retention features. Older v0.1 text below is retained as history.

# Continue SparkCert development

**Project:** [hossain0707/SparkCert](https://github.com/hossain0707/SparkCert) · **Owner:** Md Najmul Hossain · **Current state:** v0.2.0 development candidate (13 GitHub CI jobs passed, physical hardware acceptance outstanding).

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

Local-first browser/optional pywebview workbench, OpenSSH profiles/aliases, key/agent/strict host-key transport, read-only diagnostics, opt-in bounded transfer, private SSH tunnel management, limited measured HTTP model checks with concurrency, SQLite evidence integrity/retention/audit and PDF exports. It is a working codebase, **but not verified on an actual DGX Spark or clean signed installer release**.

For installation and security review, see `docs/INSTALLATION.md`, `docs/SECURITY_MODEL.md`, `docs/RELEASE_CHECKLIST.md`. The release remains unsigned and not hardware-certified.

## Next milestone

First validate SSH connectivity on physical DGX Spark from Windows/macOS/Linux over direct Ethernet, LAN and private VPN; document each configuration, negative test and measured outcome. Then fix cross-platform packaging and prioritize secure guided onboarding. See `docs/PROJECT_STATUS.md` for exact acceptance gates.
