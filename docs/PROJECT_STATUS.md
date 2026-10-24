# SparkCert — status, gaps and actionable backlog

**Snapshot:** 2026-10-25 · **Source version:** v0.1.0 · **Release label:** local-first MVP, **not** production-certified.

## Definitions

- **Implemented:** source code exists; relevant automated tests or manual local smoke tests demonstrate behavior in the development environment.
- **Partially implemented:** subset exists, but original UX or coverage is unfinished.
- **Unverified:** no conclusive cross-platform/DGX Spark test; do not advertise as supported for customers.
- **Planned:** no production implementation in project tree.

| Domain | Status | Delivered | Next acceptance criteria |
| --- | --- | --- | --- |
| Professional UI | Implemented, needs QA | Responsive navigation, cards, forms, detailed report view, animations | Full keyboard/contrast/screen-reader tests, responsive snapshots, error flows |
| Local backend | Implemented | FastAPI, loopback binding, ephemeral token, origins/CSP | Threat-model local browser/CSRF and endpoint abuse; add security regression tests |
| Windows/macOS/Linux | Unverified distribution | Python source/optional pywebview, PyInstaller CI recipe | Produce, sign where appropriate, and smoke-test native builds on each OS |
| Direct Ethernet | Partially implemented | Uses existing OS routing to SSH host | Show link/IP status and safe guidance; test real point-to-point setups |
| LAN & private VPN | Partially implemented | Supports any pre-existing routable network | Real LAN and Tailscale tests, negative failure diagnostics |
| VS Code Remote SSH config | Implemented basic import | Lists SSH Host aliases and sends to OpenSSH | Nested Include/Host edge cases and first-run UX tests |
| SSH key/agent + strict host keys | Implemented | System SSH, batch auth for probes, system terminal for interactive auth | Windows/macOS agents, keychain, enterprise policy/jump-host tests |
| SSH remote terminal | Partial | Native system terminal launched | Optional securely scoped embedded terminal, proper permission model |
| SFTP file manager | Partial | Read-only listing in home directory | Controlled upload/download, checksums, directory boundaries, transfer UX |
| GPU/system diagnostics | Implemented snapshots | hostname, OS, arch, RAM, disk, nvidia-smi, Docker, Python | DGX Spark real data, units, missing fields, unified memory fidelity |
| Infrastructure checks | Implemented heuristics | Seven checks with evidence | Configurable policies, calibration, per-target requirements |
| Model evaluations | Implemented limited | OpenAI-compatible chat, deterministic rules | Proven accuracy suites, concurrency/load, RAG evaluation and baselines |
| Model deployment, tunnel management | Planned | README manual tunnel instructions | Controlled endpoint discovery, one-click private tunnel, model preflight |
| Report persistence/PDF | Implemented | SQLite history, reportlab PDF, time/run ID | Export/import, retention, evidence integrity and cryptographic signatures |
| Recovery / factory reset | Planned | No destructive action included | Separate safe design and hardware-lab evidence before implementation |
| Remote DGX agent | Planned | No installable server agent | Consent, least privilege, auth, lifecycle and offline support |
| Enterprise governance | Planned | No RBAC, audit policy, encryption | Risk assessment, multi-user security, retention/access policy |
| Commercial production release | Not ready | No SLA, no signed release or external review | Hardware test matrix, supply-chain review, hardening, licensing |

## Product-risk and security backlog

**P0 — must complete before public production claims**

1. Cross-platform app builds verified on clean machines, with installers, code signing and macOS notarization strategy.
2. DGX Spark hardware-in-loop matrix (Ethernet, LAN, VPN, disconnected host, changed host key, password-only hosts, ProxyJump, permissions).
3. Secure remote command/file operations review, dependency audit, SBOM and pentest, local service security review.
4. Evaluation methodology: separate measured check pass rates from general readiness; benchmark measured latencies, error counts, limits and reference data.
5. Accessibility and keyboard/screen-reader tests plus reproducible UI screenshots.
6. Legal/commercial: decide OSI license vs proprietary terms; avoid official certification or NVIDIA endorsement claims.

**P1 — high-value user experience**

1. SSH connect wizard: test connectivity, guided verification of fingerprints and IPv4 direct-Ethernet setup.
2. Authenticated tunnel manager; model-endpoint discovery after SSH connect; show which traffic crosses which boundary.
3. Background jobs/progress with cancellation, streamed status and bounded resource usage.
4. Secure file transfer with checksum validation, sane path constraints, explicit action confirmations.
5. Evaluation suites: curated user datasets, batch results, versioned baselines, regression comparison, concurrency.
6. Secure audit trail and local data retention/export/redaction; avoid storing sensitive prompts by default where feasible.

**P2 — scale and value differentiation**

1. Agentless fleet readiness comparisons and change-over-time checks.
2. Optional hardened host agent for detailed GPU telemetry and server-side benchmarking.
3. Policy packs by workload and tenant; no unsupported regulatory certification language.
4. Signed evidence bundles, configurable organization branding, release gates, CI integration.
5. Recovery planning/backup inventory and test-only recovery workflows (real recovery requires hardware verification).

## Known limitations / precise wording for release notes

- 'Remote from anywhere' requires **existing** VPN or private network path and OS SSH, not an internet relay within SparkCert.
- 'Password SSH' works interactively **in native terminal**, not in background diagnostics; prefer ssh-agent.
- 'One-click' currently means save profile/evaluate, **not** device provisioning or launching a model.
- 'Production readiness score' is the pass fraction of the explicit checks performed; cannot certify an entire service or organization.
- A device can run models independently; SparkCert does not install vLLM/Ollama for v0.1.0.
- Local app database stores potentially sensitive output unencrypted; shipping to regulated customers is premature.
- Tests may use mocks and never substitute for Windows/macOS/DGX Spark hardware verification.

## Milestone closeout format for future agents

For each change, append a dated entry below describing: feature, files touched, threat/compatibility impact, exact tests and environment, test failures, screenshots, unverified systems, follow-on issue. Do **not** change statuses on assumption alone.

### 2026-10-25 — Initial source and documentation snapshot

- MVP modules present and baseline automated suite passes in this container. Features and limits were reviewed against source.
- Standalone animated architecture reference and UI motion improvements added; see `ARCHITECTURE.html`, `DESIGN_SYSTEM.md`.
- Open: physical DGX Spark validation, packaged OS builds, deeper evaluation quality, security and release gates.
