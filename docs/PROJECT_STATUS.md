# SparkCert — implementation and release status

**Source version:** v0.2.0 development candidate · **Updated:** 2026-10-25 · **Status:** functional local-first development software; **not a production-verified or certified release**.

## What is implemented and locally tested

| Subsystem | Current implementation | Verification scope / limitations |
| --- | --- | --- |
| Web and optional desktop interface | Responsive dark UI, navigation, restrained CSS motion, reduced-motion media query | Chromium offline mock-data walkthrough on 1440px desktop and 390px mobile; PyWebView native installer not verified |
| Local controller | FastAPI on 127.0.0.1 with per-process session token, origin checks, CSP | 15 automated tests locally; no independent pentest |
| SSH connection profiles | Manual host/port/user/key-path settings; OpenSSH config aliases including standard ProxyJump/key config | Mock integration tests and static review; physical Windows/Mac/Spark not tested |
| Ethernet, LAN and remote VPN | Any existing IP-reachable route via OS OpenSSH | Neither network provisioning nor Tailscale account configuration automated |
| SSH terminal / diagnostics | Native OS terminal, OpenSSH strict host keys, bounded read-only GPU/OS/system probes | Mock Linux diagnostics; remote DGX Spark measurements not obtained |
| Remote file browsing | Home-relative SSH listing, limited entries | No hostile-filesystem concurrent-modification guarantees |
| Opt-in uploads/downloads | Bounded 16 MiB, remote Python3 helper, home-scoped download, uniquely named 0700 ~/sparkcert-uploads destination | Unit/mocked API tests only; no real SFTP/hardware validation; uploads are remote filesystem writes, require operator confirmation |
| Managed private tunnels | Up to four process-local OpenSSH -N port forwards bound to 127.0.0.1; explicit stop; cleanup on exit and device deletion | Mocked lifecycle tests; forward listening does not guarantee remote API responsiveness |
| Infrastructure readiness | Seven explicit prerequisite checks with real-result report recording | Thresholds are **project heuristics**, not official NVIDIA standards |
| LLM evaluation | OpenAI-compatible chat API, 4 defined probes + custom cases, repetition 1–3, concurrency 1–4, p50/p95 latency | MockTransport tests; useful for comparison, **not an audited performance/robustness benchmark** |
| Persistence and reporting | SQLite, PDF evidence, result JSON SHA-256 check, delete/retention, local non-content audit events | Tests pass; digest not an independent digital signature; no encryption/RBAC |
| Build automation | Cross-OS Python test matrix, unsigned PyInstaller build candidates, SBOM and pip-audit workflow definitions | 13 GitHub CI jobs passed on run 40145092403; artifacts remain unsigned and require clean-machine acceptance |
| Documentation and GitHub presentation | README visuals/animation, architecture diagram, handover, tests, developer instructions | Screenshots are explicitly mock-data previews; existing GitHub metadata may require owner sidebar edit |

## Open production release gates (must not be called complete)

1. **Real hardware:** run Windows 11 x64, macOS Intel/Apple silicon, Ubuntu 24.04 against physical DGX Spark over direct Ethernet, LAN and a private remote VPN. Cover successful SSH auth, changed host key, missing key/agent, ProxyJump, closed model port, file transfer interruptions and permission denial.
2. **Native installers:** CI must actually complete on all target OS runners; smoke-test the executable on clean hardware, add artifact checksums, Windows code-signing and macOS Developer ID signing/notarization. These require appropriate certificates/accounts and explicit owner validation.
3. **Independent security:** threat model, dependency and supply-chain audit, code review/penetration test of the localhost API, SSH helper and file-transfer access; set trusted-operator boundary; mature secret protection and provenance.
4. **Enterprise-grade policy/evaluation:** per-organization policies and reference datasets; calibrated acceptance criteria, prompt-injection/RAG evaluations, realistic concurrency/load datasets, regression baselines, multi-user/RBAC support if needed.
5. **Privacy and governance:** model output currently persists unencrypted in the local SQLite database. Add stronger retention/consent controls, optional output redaction, encryption/key management strategy and signed immutable evidence if required by customers.
6. **Operational quality:** streaming/cancelable background jobs, verified error/timeout/reconnect UX, screen-reader/accessibility audit, full end-to-end browser/API test on supported hosts, professional support/update/licensing and release channels.
7. **Optional improvements:** safe device discovery with user consent, fleet scheduling, delegated agent installation after full privilege/security review, disaster recovery integrations with NVIDIA-supported tooling. No remote reset of unbootable hardware via SSH is promised.
8. **Legal/branding:** owner chooses OSI or proprietary license; keep the independent / unofficial / non-accredited disclaimer. Github About description/topics may still need a manual edit.

## Scope rules

- An SSH tunnel **only** proves that the local forwarding listener is available; it does **not** prove the model API works.
- A readiness percent means only *the named tests executed* passed. Do not call it comprehensive model safety, medical suitability, regulatory compliance or official certification.
- SHA-256 digest verification is local corruption evidence, not tamper-proof chain of custody. Back up your database before deleting reports.
- The client is local-only; there is no cloud controller, no account login, no telemetry and no credential storage.
- Password SSH is interactive in the OS terminal; automated probes need working keys/ssh-agent.

## Baseline validation

Environment: Linux container · Python 3.13 · `pytest -q`: **15 passed** · `node --check web/app.js`: **pass** · `python -m compileall -q sparkcert`: **pass** · offline Chromium screenshots: desktop/mobile **pass** using mocked API data. **No real DGX Spark, macOS or Windows acceptance tests have been performed here.**

For new workspaces start with `docs/HANDOVER_START_HERE.md` and `docs/WORKSPACE_HANDOFF.md`.


## 2026-10-25 — GitHub-hosted CI evidence

GitHub Actions run [40145092403](https://github.com/hossain0707/SparkCert/actions/runs/40145092403) completed **successfully** against commit `0d381b95de6eb6f2d2715c0de1f6bb2972efe23d`. Thirteen jobs passed: Python and JavaScript tests on Windows, macOS and Ubuntu across Python 3.11, 3.12 and 3.13 (nine combinations); pip-audit/SBOM; and unsigned desktop builds on Windows, macOS and Ubuntu (three). Build candidates and an SBOM were uploaded as workflow artifacts. CI buildability is not equivalent to validated, signed installations or actual DGX Spark end-to-end acceptance.

## 2026-10-25 — Cross-platform package distribution work (v0.2.1b1)

- Added branded desktop icon generation from local Pillow shapes for Windows ICO, macOS ICNS and PNG desktop menus; icons are produced by `scripts/generate_icons.py` within CI.
- Updated native desktop boot sequence to retain a loopback socket until Uvicorn takes ownership; waits for server startup before opening the window; shuts down server on window close.
- Added `--package-self-check` to the desktop binary. It checks bundled FastAPI routes/imports and static UI assets *without connecting to a physical device or displaying a window*. The CI packaging jobs execute this against the frozen binary.
- Added a Windows Inno Setup **per-user** EXE installer and portable ZIP, separate Apple silicon/Intel unsigned DMGs, Ubuntu 24.04 `.deb` package and portable Linux tarball.
- All release assets must be present and pass packaged-import checks before a public **pre-release** is created by CI. The release includes `SHA256SUMS.txt` and is not marked stable. Independent clean-device QA and signing/notarization remain explicitly incomplete.
- Replaced README with product-centered visual showcase, platform download table, first-connection flow, architecture, actual feature matrix, preview screenshots and continuity links.
- Local development baseline is updated with dedicated package-self-check tests. Hardware validation remains **not done**.

**Do not call this release production-ready** solely because binary packaging and import smoke tests succeed. Review `docs/RELEASE_CHECKLIST.md` and `docs/INSTALLATION.md`.
