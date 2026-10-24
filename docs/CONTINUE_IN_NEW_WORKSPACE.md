# SparkCert — copy this prompt into a new workspace or coding agent

**Attach/extract the complete `SparkCert` source archive first.** Then use:

> Continue the **SparkCert** project owned by Md Najmul Hossain. Treat the attached source as the source of truth. Before any edits, read `README.md`, `docs/WORKSPACE_HANDOFF.md`, `docs/ARCHITECTURE.md`, `docs/PROJECT_STATUS.md`, `docs/DESIGN_SYSTEM.md`, `docs/PRODUCT_ROADMAP.md`, and `docs/VERIFICATION.md`; inspect existing code and tests; then run the baseline tests. Preserve implemented behavior and secure defaults. Do not claim unfinished features are working or that NVIDIA endorses the product. Our goal is a production-grade, cross-platform, local-first **AI readiness evaluation** application for DGX Spark and generic Linux inference hosts. Users need easy Ethernet/LAN/private VPN connectivity, VS Code-compatible OpenSSH alias/key/agent/ProxyJump connections, honest diagnostics, robust AI model evaluations, evidence reports and a premium, tastefully animated accessible UI. Prioritize the highest-risk incomplete work listed in `PROJECT_STATUS.md`; add targeted tests and record exactly what passed on which platform/device. Never fabricate measurements, score reliability from untested criteria, store credentials in code, silently install privileged agents or expose local services to public networks. Update project documentation, especially `docs/WORKSPACE_HANDOFF.md`, status and verification ledger, before ending. Keep development using free and open-source tools unless explicitly authorized otherwise. Provide the actual changed files, tests run, remaining blockers, and revised handoff archive.

## Baseline context the next agent must preserve

- Current release is **v0.1.0 MVP, not production-grade verified**.
- Current UI is FastAPI-served local HTML/JS/CSS with optional **pywebview**, NOT Tauri/React.
- OpenSSH runs on the operator computer; app uses its alias/key/known_hosts/agent settings. No custom SSH protocol implementation.
- Direct Ethernet/VPN are network transport options, **not** automatically configured by the app.
- SSH terminal opens the OS terminal; file browsing is read-only.
- Model tests target an already-running OpenAI-compatible HTTP API, potentially through a *manual* SSH tunnel.
- SQLite saves reports (including model outputs); API keys and SSH private key contents are not stored. DB is not encrypted.
- PDF assessment scores refer **only** to executed named checks; no official certification or accreditation.
- Packaging CI exists as a **recipe**, not as verified signed native installers.
- Animation is UI enhancement, not proof of activity; always respect reduced-motion preferences.
- No real physical DGX Spark tests were performed here.

## Continuity protocol

1. Start new work from a *new feature branch* or a clean source snapshot; do not discard docs or previous code.
2. Record the new workspace's environment and baseline tests in `docs/VERIFICATION.md`.
3. Maintain exact `Implemented / Partial / Planned / Unverified` status and acceptance criteria in `docs/PROJECT_STATUS.md`.
4. For each milestone, document decisions, test evidence and remaining blockers in `docs/WORKSPACE_HANDOFF.md`.
5. Package the complete source (without `.venv`, `.git`, credentials, `~/.ssh`, DB and `__pycache__`) and preserve the updated handoff after every milestone.
