> **Current project: v0.2.0 development candidate, NOT production validated.** See `docs/PROJECT_STATUS.md`, `docs/VERIFICATION.md`, `docs/WORKSPACE_HANDOFF.md` and `CHANGELOG.md` for new tunnel, file transfer, evaluation and retention features. Older v0.1 text below is retained as history.

# SparkCert — Start Here / Cross-Workspace Project Handover

**Owner:** Md Najmul Hossain  
**Repository:** https://github.com/hossain0707/SparkCert  
**Release state:** v0.1.0 development MVP (2026-10-25)  
**Source of truth:** This repository, tagged releases, tests, and traceable evidence. Do not treat screenshots or conversations as proof of a completed feature.

> **MANDATORY FOR ANY FUTURE AGENT/DEVELOPER:** Read this document, `README.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN_SYSTEM.md`, `docs/PRODUCT_ROADMAP.md`, and inspect actual source/tests before changing anything. Never claim production readiness without validation on real target hardware. Preserve the local-first, safe-by-default design.

## Vision

SparkCert is a professional, cross-platform AI production-readiness workbench for NVIDIA DGX Spark and other SSH-managed AI/Linux hosts. It reduces complexity for Windows/macOS/Linux users who connect over direct Ethernet, local LAN, or private VPN, including reuse of VS Code/OpenSSH profiles. Its business differentiator is transparent AI application validation and evidence reporting, **not** claiming official NVIDIA or compliance certification.

## Status at handover

| Area | Actual implementation | Current limits | Priority |
|---|---|---|---|
| Responsive UI | Dashboard, Connections, Evaluations, Reports, Security/About | No formal UX or accessibility audit | P2 |
| Visual design | Dark premium UI; custom SVG icons, responsive cards, status tags | Add purposeful subtle motion with reduced-motion support | P2 |
| Local backend | FastAPI, loopback-only server, random process token, input validation | Threat model, dependency audit and adversarial tests pending | P0 |
| Saved connections | SQLite profiles; import OpenSSH aliases | No LAN autodiscovery, no step-by-step fingerprint wizard | P1 |
| SSH transport | System OpenSSH; aliases/keys/ssh-agent/ProxyJump supported via OpenSSH | Windows/macOS field testing pending, no built-in interactive password entry | P0 |
| Direct Ethernet/LAN/VPN | Works when underlying network and SSH work | Network auto-configuration not implemented | P1 |
| Remote terminal | Launches host terminal with ssh | No embedded terminal emulator | P2 |
| Remote file browser | Read-only directory listing under remote home | No transfer/edit/delete | P2 |
| Remote monitoring | Read-only nvidia-smi/Linux/Docker/Python probes | Snapshot only, no streaming graphs | P1 |
| Infrastructure readiness | 7 documented checks, measured pass percentages | Heuristic thresholds; no official safety/compliance certificate | P1 |
| Model evaluation | Live OpenAI-compatible API, 4 starter checks plus custom tests | No broad safety certification, load/concurrency, RAG quality suite | P1 |
| Evidence reports | Run history in SQLite and PDF export | No signed provenance or retention controls | P1 |
| Desktop wrapper | pywebview launcher + PyInstaller CI recipes | Unsigned artifacts, untested native installers | P0 |
| Automated tests | 9 tests passed locally with pytest | No real DGX Spark hardware/E2E test report | P0 |
| Production maturity | v0.1.0 MVP | **NOT production certified, audited or customer-ready** | P0 |

## Explicitly not completed

- No real DGX Spark end-to-end acceptance test has been documented in this work session.
- No verified Windows EXE/macOS DMG/Linux executable distributed or code signed.
- No agent installed on DGX Spark, no unattended provisioning, no live streaming telemetry.
- No integrated one-click VPN provisioning or Ethernet IP setup.
- No automatic SSH port-forward tunnel managed from the UI (manual command documented).
- No SFTP upload/download, no remote file mutation, no factory reset, no unattended recovery.
- No external regulatory, NVIDIA-authorized, third-party or accredited certification.
- No proof that broader model safety/hallucination testing is comprehensive.
- No commercial license, subscription, updater, support agreements, or cloud architecture.

## Runtime architectural boundaries

1. **Control plane (Windows/macOS/Linux):** local browser or pywebview runs the UI and a loopback FastAPI API. Data and report history live locally under `~/.sparkcert`.
2. **Host connection:** app delegates SSH authentication/known-host checks to the OS OpenSSH client; remote operations are predefined, read-only diagnostic scripts.
3. **Evaluation plane:** app sends explicit HTTP requests to the *user-configured* OpenAI-compatible model API, often over a separately established SSH tunnel. Do not claim evaluation necessarily runs inside DGX Spark.
4. **No hidden cloud:** app has no telemetry or remote cloud service by default. Connecting an external AI endpoint can transmit prompts to that endpoint; user must understand the destination.
5. **Security boundary:** never run a web server on 0.0.0.0 by default; never skip SSH host-key checks; never persist SSH passwords/private key material/API keys.

## Repository map

```text
SparkCert/
├── README.md                    Product overview, supported usage, caveats
├── pyproject.toml               Python dependencies and entry point
├── desktop_launcher.py          Desktop packaging entrypoint
├── sparkcert/
│   ├── app.py                   Local HTTP API / auth / request validation
│   ├── ssh.py                   OpenSSH and read-only remote health checks
│   ├── evaluation.py            Model API probes and scoring
│   ├── reports.py               PDF report generation
│   ├── store.py                 SQLite persistent store
│   ├── __main__.py              Browser/local app bootstrap
│   └── __main_desktop__.py      pywebview desktop wrapper
├── web/
│   ├── index.html               UI structure / SVG symbol set
│   ├── app.js                   Navigation, forms, API orchestration
│   └── styles.css               Design system, layouts, responsive styles
├── tests/test_core.py           Unit and API tests
├── docs/
│   ├── HANDOVER_START_HERE.md   This document
│   ├── ARCHITECTURE.md          Technical dataflows and interfaces
│   ├── DESIGN_SYSTEM.md         Visual/motion specification
│   ├── ARCHITECTURE.html         Interactive, responsive architecture diagram
│   └── PRODUCT_ROADMAP.md       Required production steps
└── .github/workflows/ci.yml    Unit tests and desktop build matrix
```

## Safe developer bootstrap

```bash
python -m venv .venv
# Unix: source .venv/bin/activate
# Windows: .venv\\Scripts\\Activate.ps1
python -m pip install -e '.[dev]'
pytest -q
node --check web/app.js
python -m sparkcert
```

The local UI opens in a browser. For optional desktop wrapper, install `.[desktop]` and run `python -m sparkcert.__main_desktop__`.

## Next development sequence

**P0** Re-run tests and perform a real DGX Spark connection test with evidence over Ethernet/LAN/VPN; validate OpenSSH host key, alias/ProxyJump, Windows/macOS behavior; build/launch all three desktop packages; fix any packaging/security defects. **P1** Guided onboarding, auto-diagnostics, model endpoint tunnel management, robust test suite, detailed evidentiary reports, explicit data protection controls. **P2** Refine polished micro-interactions with reduced-motion support; CI E2E accessibility checks, design assets, optional live graphs. **P3** Commercial readiness, SBOM, signing/notarization, enterprise policy, security review, licensing and support.

## Engineering acceptance gate

A task is only 'done' when source, tests, supported OS/hardware evidence, documentation and security constraints align. A feature visible in the UI but without executable implementation must be labeled demo/planned. **Never fabricate benchmark scores, certification grades, SSH success, installer compatibility or third-party approval.**

## Notes for agents in a fresh workspace

Start by reading this and doing a repository tree inspection. Confirm which files are present and GitHub branch state, then run local tests. Track changes in `docs/DEVELOPMENT_LOG.md` with date, commit, tested environment, evidence, unresolved issues and next actions. Preserve attribution: © 2026 Md Najmul Hossain. Avoid emojis in README and maintain the existing independent/unofficial NVIDIA disclaimer. Do not use paid cloud services without authorization. No secret material in commits.
