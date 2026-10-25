# SparkCert — release qualification checklist

**Version in scope:** v0.2.0 development candidate · **Owner:** Md Najmul Hossain.

This checklist is a **release gate**, not a promise that features are production-ready. An unchecked item must remain unchecked until reproducible evidence exists.

## Proven engineering checks

- [x] Local Python unit/API suite: 15 passed, Linux/Python 3.13.
- [x] JS source parse, Python `compileall`.
- [x] Mock-only Chromium page traversal at desktop 1440px and mobile 390px without visible JS exceptions or horizontal layout overflow.
- [x] Local Uvicorn `GET /api/health` returned 200; unauthenticated `GET /api/devices` returned 401.
- [x] GitHub-hosted [CI run 40145092403](https://github.com/hossain0707/SparkCert/actions/runs/40145092403): **13 jobs successful** across Windows/macOS/Linux, 3 Python versions, security inventory and unsigned build artifacts.

## Hardware and distribution gates — NOT VERIFIED

- [ ] Windows 11 clean install and unsigned prototype launch; document SmartScreen behavior.
- [ ] Windows signed Authenticode release using maintainer-controlled certificate.
- [ ] macOS Apple silicon clean install; macOS Intel clean install.
- [ ] macOS Developer ID signature and Apple notarization.
- [ ] Ubuntu 24.04 clean installation, permissions, webview dependencies and SSH availability.
- [ ] Physical DGX Spark Ethernet cable test, wired LAN test and private remote VPN test.
- [ ] Real SSH key, ssh-agent, `~/.ssh/config`, Include/ProxyJump, password-only host and fingerprint mismatch.
- [ ] Real tunnel opens/closes correctly with GPU model API and missing/closed target port.
- [ ] Real 16 MiB file upload/download tests, symlink/path escape/interrupt/security checks.
- [ ] Inference tests against actual local model, latency calibration and reference metrics.
- [ ] Cross-platform accessibility and keyboard/screen-reader audit.
- [ ] Independent threat model and penetration test; confirm no external telemetry or credential leaks.
- [ ] Dependency audit/SBOM evidence captured in release; security updates validated.
- [ ] Data deletion, retention and secure backups/export policy for sensitive prompts/responses.
- [ ] Signed release packages, reproducible checksums, rollout/rollback instructions and documented support channel.
- [ ] Chosen source code license/commercial terms and trademark/legal review.

## Never state without evidence

- "100% production-ready", "certified by NVIDIA", "regulatory compliant", "secure for medical data", or "DGX Spark tested on every platform".
- A successful mocked test is not a real SSH transport test.
- A listening tunnel is not proof a remote model server is healthy.
- The v0.2 SHA-256 evidence digest is not a cryptographic signature.

## Distribution policy

The CI artifacts are **unsigned build candidates**. They may be used by the owner for controlled QA, but are not recommended as customer production installers. Do not create an official stable GitHub Release until the hardware, security and distribution gates are documented.
