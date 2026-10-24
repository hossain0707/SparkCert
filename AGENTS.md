# SparkCert agent instructions

**Project:** SparkCert — local-first AI readiness workbench for NVIDIA DGX Spark and other SSH-managed Linux AI hosts.  
**Owner:** Md Najmul Hossain  
**Status:** Development MVP v0.1.0; not an independently validated production release.

## Mandatory first steps (in every new workspace)

1. Read `docs/HANDOVER_START_HERE.md`, `docs/WORKSPACE_HANDOFF.md`, `docs/PROJECT_STATUS.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN_SYSTEM.md`, `docs/PRODUCT_ROADMAP.md`, `docs/VERIFICATION.md`, and `docs/CONTINUE_IN_NEW_WORKSPACE.md`.
2. Inspect the actual source tree, current git status, GitHub default branch and recent commits. Do **not** assume docs and code match without checking.
3. Run `python -m pip install -e '.[dev]'`, `python -m pytest -q`, and `node --check web/app.js` before changes. Record deviations.
4. Select work from the highest-priority unfinished items in `docs/PROJECT_STATUS.md`. Do not claim unverified OS/hardware capabilities are working.
5. Prefer small, reviewable changes, specific tests, and updated docs. Record measured verification evidence and any new risks in `docs/DEVELOPMENT_LOG.md` or `docs/VERIFICATION.md`.

## Guardrails

- **No fabricated benchmark results, false connected/offline indicators, or official NVIDIA/regulatory certification claims.**
- Preserve local-first architecture and localhost-only backend; no public exposure of SSH or local HTTP ports by default.
- Never disable OpenSSH host-key verification or store passwords, private keys, service credentials, tokens or personally identifiable sample data in git.
- No shell injection, arbitrary remote scripts, destructive SSH commands, auto-reset, agent install or remote file mutation without separately reviewed design, explicit consent, safeguards and tests.
- DGX Spark remote access relies on existing Ethernet/LAN/private VPN, available SSH account and verified host fingerprint; it cannot recover a device that is offline/unbootable solely via SSH.
- Preserve distinction between architecture *implemented today* and capabilities *planned for later*.
- Use free and open-source development tools where possible. No paid service without authorization.

## Design contract

Professional restrained dark UI, credible telemetry, distinct empty/error/loading states, fine SVG iconography, clear evidence scope, responsive layout, subtle meaningful animation and full `prefers-reduced-motion` support. The visually interactive overview lives in `docs/ARCHITECTURE.html`; visual specifications are in `docs/DESIGN_SYSTEM.md`. Do not introduce cartoon UI, distracting motion, gratuitous emojis or fake device data without prominent demo labels.

## Completion report

For each milestone explain: changed files, why, test commands and results, OS/device model/OS version verified, security/privacy impacts, remaining P0/P1 risks, updated handover entry, and a commit hash or PR link. Only mark a capability production-ready when corresponding validation gates are met.
