# SparkCert engineering, validation and release roadmap

## Current deliverable status — v0.1.0

A *working local-first MVP*, with validated API/database/PDF units and functional SSH integration paths; NOT an independently verified production-grade commercial product. The architecture is designed to grow into that standard.

### Completed
- Polished, responsive interface with dashboard, connections, evaluator, reports, security information
- OpenSSH alias import and profile persistence with strict host key checking
- Read-only live host/GPU/Docker/system diagnostics and infrastructure readiness report
- Local AI model evaluation through OpenAI-compatible HTTP API with transparent deterministic judgments
- PDF evidence export, SQLite history, input validation, API token/origin protections
- Native terminal launch hooks and read-only remote file browsing
- Automated regression tests and cross-platform desktop packaging build recipes

### Required before a public production release
1. Validate Windows 11, macOS Apple silicon/Intel, Ubuntu 24.04 installers from CI, including WebView2/WebKit dependencies and signing/notarization.
2. Run hardware-in-the-loop tests on multiple DGX Spark OS revisions, over direct Ethernet, LAN, Tailscale, SSH ProxyJump, and SSH agents.
3. Complete UI accessibility audit (keyboard navigation, screen readers, contrast) and end-to-end UI test automation.
4. Add real audit log, database encryption/key management policy, retention management, optional OS-keychain secret integration, role-based access for teams.
5. Add optional isolated agent on remote hosts for continuous monitoring, streaming test progress and server-side GPU benchmarking.
6. Add target discovery, model launch/deployment, Docker-based sandboxing and preflight checks with explicit consent/rollback.
7. Add guarded, fully tested SFTP transfers with limits and checksum verification; decide organizational requirements for filesystem access.
8. Add organizational policy packs and extensible evaluation datasets; calibrate thresholds against real use cases.
9. Benchmark load/concurrency and multi-turn RAG with reference data and proper accuracy measures; no "certification" claims without an accredited framework.
10. Conduct third-party security review, threat modeling, update-signing, SBOM, dependency scanning, fuzz testing, supply-chain hardening, and formal releases.
11. Add a proper license only after the owner decides free/commercial distribution terms.

## Proposed next releases

- **v0.2**: Secure device onboarding wizard, known-host fingerprint verification, signed desktop builds, diagnostics test matrix and documented first-party Spark setup.
- **v0.3**: SSH reverse/forward tunnels from UI, one-click endpoint selection, model inventory, robust server-side benchmarking and GPU memory monitoring.
- **v0.4**: Policy evaluation profiles, per-organization baselines, tests for retrieval quality, hallucination on vetted questions, concurrency and regression.
- **v1.0**: Validated installability, enterprise security controls, real-device lab, load testing, extensibility API, release/support plan.

## Product differentiator

NVIDIA Sync already handles SSH connection management, tunneling, application launch, and resource monitoring. SparkCert should invest primarily in **evidence-backed AI application readiness and reproducibility**, not rebuild Sync or present generic remote monitoring as novel.

## Engineering standards

- Default-deny outbound/cloud integration, least privilege, no remote sudo calls by default.
- Every check records exact test definition, measured result, time, environment and limitations.
- No fabricated GPU performance statistics, official certifications, or untested "production ready" badges.
- All destructive operations are excluded until independently vetted with explicit backups, confirmation, rollback and test fixtures.
