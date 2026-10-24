# SparkCert — canonical workspace handoff

> **READ THIS FIRST in any new chat, coding agent, or computer.**
> Snapshot: 2026-10-25 (Asia/Seoul). Project: SparkCert. Owner: Md Najmul Hossain. Version in source: `0.1.0`.
> Status: working and locally tested **MVP**, **NOT** a production-certified, publicly distributed, or real-DGX-Spark-validated application.

## 1. Intent and non-negotiable decisions

SparkCert is an **independent, local-first AI production-readiness assessment workbench** for NVIDIA DGX Spark and other SSH-managed Linux inference hosts. The core business problem is collecting **real**, repeatable evidence about infrastructure prerequisites and AI model/application behavior, then producing useful, attributable readiness reports. The name “Cert” does **not** mean NVIDIA endorsement, external accreditation, or legal/regulatory certification.

Requested end-user experience:

1. Install on **Windows / macOS / Linux**.
2. Connect to DGX Spark using **direct Ethernet, a LAN, or private remote VPN**, with the same **OpenSSH aliases, keys, ProxyJump and ssh-agent settings as VS Code Remote SSH**.
3. View system/GPU diagnostics; interact with remote shell; browse files safely.
4. Evaluate a privately served LLM through an OpenAI-compatible API; retain evidence and export PDF.
5. Later: fleet management, guided agent installation, richer evaluations, file transfers, remote tunnels and carefully scoped disaster recovery.

Constraints: **no forced cloud account, no telemetry, no paid third-party dependency, and no fake test results**; secure-by-default, minimal privilege, clear confirmations before any destructive action, clear differentiation between implementation and intention. Use Python/React/Tauri only when justified; existing implementation is FastAPI + dependency-free JS/CSS with optional pywebview desktop window. Do not rewrite stable working functionality without evidence.

## 2. What exists today, verified in source

| Capability | Status | How/limitations |
| --- | --- | --- |
| Responsive dark desktop-style app | **Implemented** | `web/index.html`, `web/styles.css`, `web/app.js`; UI motion honors reduced-motion preference |
| Local server | **Implemented** | `sparkcert/app.py`, Uvicorn, localhost-only `127.0.0.1` with ephemeral per-run API token |
| Desktop window | **Implemented source, packaging unverified** | `sparkcert/__main_desktop__.py` with optional pywebview; not native Tauri; no signed installers shipped |
| Cross-platform install | **Source-install supported, cross-OS hardware unverified** | `pyproject.toml`, Python 3.11+, system OpenSSH, optional desktop dependency |
| Direct Ethernet | **Uses OS networking; no automatic setup** | Configure a reachable IP and host route; physically connect and verify device |
| LAN/Wi-Fi | **Uses existing network** | Must be routable to TCP port 22; Spark SSH enabled |
| Remote access | **Uses existing VPN/network route** | Does **not** provision/manage Tailscale or public relay; never expose SSH publicly as default |
| VS Code/OpenSSH import | **Implemented (Host alias parser)** | `sparkcert/ssh.py::config_aliases()`, using OS OpenSSH for actual resolution; no VS Code extension integration |
| SSH profile CRUD | **Implemented** | `sparkcert/store.py`; alias/manual host, username, port and key path; no secret content persisted |
| SSH key/agent + host validation | **Implemented** | Uses system `ssh`; strict `known_hosts`; new fingerprints must be independently checked |
| Password-authenticated remote shell | **System terminal only** | No embedded password prompt; background diagnostics require key/agent batch auth |
| Embedded terminal | **Not implemented** | Opens native system terminal via `open_terminal()`; not a terminal inside UI |
| SSH diagnostics | **Implemented** | `health_probe()` via predefined read-only remote commands; sampled (not live-streamed) |
| Infrastructure assessment | **Implemented** | 7 heuristic checks (SSH, Linux, GPU, RAM, disk, Python, Docker); this is not formal compliance |
| Remote file browser | **Read-only implemented** | Home-directory scoped listing; no uploads/downloads yet |
| OpenAI-compatible model evaluation | **Implemented** | 4 basic test cases + custom cases; endpoint must be independently reachable; no remote model installation |
| PDF evidence reports + history | **Implemented** | `sparkcert/reports.py`, `sparkcert/store.py`; local SQLite, unencrypted results |
| Local security controls | **Partially implemented** | Loopback, token, origin check, escaping, strict SSH, no stored API keys; no audit/security review |
| Native installer build recipes | **Present, unverified** | `.github/workflows/ci.yml` matrix Windows/macOS/Linux; signing/notarization missing |
| Remote evaluation agent / continuous monitoring | **Not implemented** | Future milestone |
| One-click model service deployment/tunnel | **Not implemented** | Manual SSH tunnel in README; model must already be running |
| Deep red-team, RAG, hallucination, concurrency | **Not implemented** | Existing deterministic probes are intentionally limited |
| Remote OS recovery/reset | **Not implemented** | Do not promise remote reset of unbootable hardware |
| Public production-grade verification | **Not completed** | No hardware lab, no actual signed distributions, penetration test, SBOM, independent review |

## 3. Directory map

```text
SparkCert/
├── README.md                      # main getting-started and implemented scope
├── pyproject.toml                 # Python package/dependencies
├── LICENSE-NOTICE.md             # copyright/trademark; licensing decision pending
├── desktop_launcher.py           # PyInstaller entry point
├── sparkcert/
│   ├── __main__.py                # local browser launcher (python -m sparkcert)
│   ├── __main_desktop__.py        # optional pywebview window
│   ├── app.py                     # FastAPI endpoints and request boundaries
│   ├── ssh.py                     # SSH config parsing, diagnostics, shell and file listing
│   ├── evaluation.py              # deterministic LLM test engine / validators
│   ├── store.py                   # SQLite persistence
│   └── reports.py                 # reportlab PDF rendering
├── web/
│   ├── index.html                 # application shell/nav/icons
│   ├── styles.css                 # responsive design and accessible motion
│   └── app.js                     # SPA page rendering, state and API requests
├── tests/test_core.py            # tests for API, security, SSH, evaluation, reporting
├── .github/workflows/ci.yml      # test + desktop build recipe (not certified output)
└── docs/
    ├── WORKSPACE_HANDOFF.md      # THIS FILE; all decisions and continuation steps
    ├── PROJECT_STATUS.md         # feature status and prioritized remaining backlog
    ├── ARCHITECTURE.md           # actual runtime/data flow, trust boundaries, API inventory
    ├── DESIGN_SYSTEM.md          # UI/interaction/motion requirements
    ├── PRODUCT_ROADMAP.md        # next releases and gates
    ├── VERIFICATION.md           # tests/release verification and hardware matrix
    ├── CONTINUE_IN_NEW_WORKSPACE.md # copy/paste follow-on task prompt
    └── ARCHITECTURE.html         # portable animated, standalone interactive architecture
```

## 4. Start and test

```bash
cd SparkCert
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m pytest -q
node --check web/app.js       # optional; requires Node.js
python -m sparkcert          # opens http://127.0.0.1:<random-port>/
```

Optional desktop native-window dependency: `python -m pip install -e '.[desktop]'` then `python -m sparkcert.__main_desktop__`. Windows installer/macOS DMG must be built, manually tested and signed before claiming release readiness. Diagram: open `docs/ARCHITECTURE.html` in a browser, without installing dependencies.

## 5. Architectural invariants

- All app HTTP routes bind loopback only; never expose this service to a public interface without a separate authorization design.
- The app invokes the **local system OpenSSH client**, not a reimplemented SSH stack; standard `~/.ssh/config`, ssh-agent, `known_hosts`, key paths and jump hosts remain with the OS.
- SSH diagnostics are read-only and predefined; no general remote command execution API in `app.py`.
- Remote terminal opens OS terminal; it is **not** an integrated browser shell.
- For model tests, UI -> localhost API -> external model endpoint directly. An SSH tunnel must be established outside the UI if the model API is available only on the Spark. No agent is installed by v0.1.0.
- Only results from executed tests can produce scores. Do not show placeholders as live telemetry.
- Report percentages apply **only to selected tests**, not general AI reliability or security certifications.
- The local DB stores model output and evidence; PDFs/DB should be treated as potentially sensitive even though SSH passwords/private key contents/API keys are not persisted.
- All feature claims need a passing test or explicit "not verified" qualification.

## 6. Design constraints

High-quality professional dark UI; deep blue-black canvas, jade/teal highlight, typographic hierarchy, generous spacing, crisp outlines, accessible forms, strong empty/error/loading states. Use restrained animation: page transitions, topology links, status activity when backed by *real* status, button hover, modals, progress for actual tasks. **No fake GPU utilization animation**, excessive motion, decorative parallax, blocking transitions, or unbounded animation. Honor `prefers-reduced-motion`, test narrow/mobile screens and keyboard navigation. Details in `DESIGN_SYSTEM.md`.

## 7. Top priorities for next agent (in order)

1. **Baseline**: read the actual code and docs before edits. Run `pytest -q` and `node --check web/app.js`, record versions and failures. Ensure no secrets in staged artifacts.
2. **Real cross-platform/real-device validation**: Windows 11, macOS ARM/Intel, Ubuntu; Ethernet/LAN/VPN; DGX Spark versions; SSH keys/agents/ProxyJump, fingerprint mismatch and failure-path testing.
3. **Automated UI tests and accessibility** (keyboard, contrast, screen reader, reduced-motion). Add Playwright tests if environment permits and take screenshots for regressions.
4. **SSH onboarding**: managed first-connection fingerprint verification (never auto-accept), better networking guidance and one-click test; ideally add secure UI-initiated tunnel support.
5. **Evaluation expansion**: model discovery/inventory and realistic, validated performance/concurrency; curated RAG, prompt-injection and regression suites with appropriate metrics and evidence.
6. **Trust/production hardening**: OS credential storage, audit logs, backup/retention controls, database encryption threat model, release signature, dependency/SBOM scanning, external security testing.
7. **Packaged release**: actual working Windows/macOS/Linux installer artifacts, smoke-tested and signed/notarized where appropriate; decide license/commercial distribution terms.
8. **Optional device agent**: independently designed agent with explicit install/uninstall, least privilege and secure authenticated protocol; no silent remote installation.

See `PROJECT_STATUS.md` for exact feature-by-feature acceptance criteria and priority.

## 8. Copying to another workspace / non-loss guarantee

- **Download the entire `SparkCert` source archive**, not just screenshots or README. All logic, tests, architecture, UI styles and this handoff are inside it.
- Put this folder into another workspace/repo and ask the next agent to read `docs/WORKSPACE_HANDOFF.md`, `docs/ARCHITECTURE.md`, `docs/PROJECT_STATUS.md` and `docs/CONTINUE_IN_NEW_WORKSPACE.md` before changing code.
- **No GitHub push/hosting is implied** by this handoff. A ZIP is a point-in-time copy; committing/pushing to an owned repository is a separate intentional action.
- **Runtime data is not included in the source archive**: per-machine DB is under `~/.sparkcert/sparkcert.db`, SSH keys/config/known_hosts under the user's OS profile. Back these up separately using approved methods. Do not embed credentials or personal data into source control.
- Keep a new dated handoff update after every milestone with test results, changed files, architecture decisions, and next steps.

## 9. Business/product positioning

SparkCert is a cross-platform control plane for verifiable local AI readiness: **host prerequisite checks + narrow model-behavior tests + stored evidence + reproducible reports**. It is not a replacement for NVIDIA Sync or a claimed NVIDIA-endorsed certification service. First support Spark; build a generic SSH/OpenAI-compatible backend so the addressable market includes non-Spark inference hosts. Freemium/commercial pricing remains a hypothesis, not a verified business model.


## README showcase and GitHub profile update — 2026-10-25

The repository README now embeds **three version-controlled SVG assets**:

1. \`assets/sparkcert-hero.svg\` — branded overview hero with truthful v0.1.0 MVP labeling.
2. \`assets/sparkcert-workflow-animated.svg\` — CSS-animated four-stage **illustrative** tour (Connect → Inspect → Evaluate → Report); includes reduced-motion support, not real hardware or screen-recording evidence.
3. \`assets/sparkcert-architecture.svg\` — diagram of the **implemented** local-controller architecture; subtle animated paths represent logical data movement only.

The README also links to \`docs/ARCHITECTURE.md\`, \`docs/DESIGN_SYSTEM.md\`, \`docs/PROJECT_STATUS.md\`, \`docs/VERIFICATION.md\`, and this handoff so future workspaces can continue with full context.

GitHub repository sidebar **About** description and topics require a separate repository-metadata edit; committing markdown does not change them. The exact suggested metadata and owner instructions are in \`docs/REPOSITORY_PROFILE.md\`. Do not claim those sidebar settings were applied unless independently verified.

**Verification:** original Python automated test suite: 9 passed; \`node --check web/app.js\` completed successfully in the current Linux workspace. GitHub source-file links and asset contents were fetched from the updated \`main\` branch. Animated SVG should be reviewed visually on the public GitHub README; no real DGX Spark connection, signed installer, hardware evaluation, or customer acceptance testing was performed as part of this documentation update.
