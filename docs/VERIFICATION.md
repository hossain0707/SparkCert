# SparkCert verification and release ledger

Record outcomes **actually executed**, not expected outcomes. Reference baseline: 2026-10-25, Linux container, Python 3.13, pytest 9.0.2.

## Local reproducible commands

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
node --check web/app.js
python -m sparkcert --no-browser  # smoke check in separate terminal
```

## Automated coverage

- FastAPI token and origin rejection, content security policy header.
- Device create/read/delete and PDF report persistence (SSH dependency mocked).
- SSH injection-unsafe host input validation, strict SSH option generation, alias parsing.
- GPU unified memory/host diagnostics parse and seven-check score (remote SSH mocked).
- Deterministic expected-output comparisons and invalid endpoint rejection.
- Live HTTP evaluation call path through a mock OpenAI-compatible HTTP transport.

## Hardware and OS manual test matrix — NOT EXECUTED in this workspace

| Platform/path | Clean install | Saved SSH alias | Strict host key | Diagnostics | Evaluation | PDF | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Windows 11 x64 + Ethernet | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| Windows 11 x64 + LAN | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| macOS Apple silicon + Ethernet | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| macOS Intel + LAN | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| Ubuntu 24.04 + LAN | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| VPN remote route (Tailscale) | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| ProxyJump/bastion host | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |
| NVIDIA DGX Spark actual device | TODO | TODO | TODO | TODO | TODO | TODO | **UNVERIFIED** |

Do not promote any row to pass until exercised on that real platform. Important negative cases: no SSH service, DNS error, fingerprint mismatch, password-only host, SSH agent unavailable, missing `nvidia-smi`, missing Docker, low disk/RAM, invalid API response, model timeout, inaccessible endpoint, PDF export error, interruption during test.

## Production release gates

- Packaging: installers produced and installed in clean VMs/machines; macOS notarization/signing, Windows Authenticode or documented equivalent trust plan.
- Security: threat model, local HTTP loopback exposure test, dependency scan/SBOM, fuzz, third-party review of remote execution/file handling, log redaction.
- Safety: no remote destructive action without privilege scoping, confirmed backups, explicit confirmation and tested recovery rollback.
- UX/accessibility: WCAG AA verification, keyboard paths, zoom/motion, screen-reader and dark-mode contrast, localization as needed.
- Evidence quality: official external 'certified' language **never used** without accredited framework; tests/calibration and limitations specified in every report.
- Privacy: data retention, delete/export, keychain/policy, encryption threat model for saved outputs.
- Operations: versioned release notes, source/artifact provenance, update signing, license and support policy.

## 2026-10-25 UI verification performed in this container

- **Pass:** Chromium headless rendered the app with offline stubbed API responses via injected JavaScript (no actual SSH or HTTP requests); overview to Architecture and Connections navigation worked without JavaScript exceptions.
- **Pass:** 390px mobile viewport opened the navigation, displayed the Architecture page, and honored `prefers-reduced-motion: reduce`.
- **Pass:** standalone `docs/ARCHITECTURE.html` rendered in headless Chromium and its **Pause diagram motion** control toggled state.
- Screenshots: `docs/assets/overview-preview.png` (initial MVP visual); `docs/assets/architecture-preview.png`, `docs/assets/architecture-mobile-preview.png`, `docs/assets/standalone-blueprint-preview.png` (dated architecture visuals).
- **Environment limitation:** Chromium browser navigation to localhost and `file:` URLs was blocked by container administrative policy (`net::ERR_BLOCKED_BY_ADMINISTRATOR`). The UI smoke test therefore used an offline HTML/CSS/JS rendering harness with mocked API responses. FastAPI/PDF/SSH logic has separate Python test coverage; **end-to-end browser-to-server-on-network testing remains unverified**.
- Repeatable commands: `python -m pytest -q` → **9 passed**; `node --check web/app.js` → **pass**. No DGX Spark hardware access was performed.

## 2026-10-25 — v0.2.0 development upgrade; actual execution evidence

- `python -m pytest -q`: **15 passed**, on this Linux Python 3.13 environment.
- `node --check web/app.js`: **pass**.
- `python -m compileall -q sparkcert`: **pass**.
- `python scripts/ui_smoke.py`: **pass**, offline Chromium at 1440 × 900 and 390 × 844; navigated Connections → AI Evaluations → Settings; asserted tunnel/evaluation/retention forms, no JS exceptions or horizontal viewport overflow. Explicitly **mock data** and injected API stubs. Screenshots: `docs/assets/v02-desktop-settings-preview.png`, `docs/assets/v02-mobile-settings-preview.png`.
- Automated tests cover tunnel construction/shutdown through mocked Popen/socket, permissions, bounded file upload/download through mocked remote helper, repeat/concurrent evaluation MockTransport, SHA-256 tampering blocking PDF, report deletion and age-based purge.
- **Not executed:** real SSH transport (OpenSSH client is not installed in this container), physical DGX Spark connection, Ethernet/VPN end-to-end, Windows/macOS PyInstaller build, CI cloud runners, vulnerability audit tool, SBOM command, signed distribution or external penetration test.

No '100% production-ready' or external certification claim can be made on this evidence.


## 2026-10-25 — GitHub-hosted CI evidence

GitHub Actions run [40145092403](https://github.com/hossain0707/SparkCert/actions/runs/40145092403) completed **successfully** against commit `0d381b95de6eb6f2d2715c0de1f6bb2972efe23d`. Thirteen jobs passed: Python/JavaScript tests on Windows, macOS and Ubuntu with Python 3.11, 3.12 and 3.13 (nine combinations); a pip-audit/SBOM job; and unsigned desktop build jobs on each OS (three). Artifacts were produced: Windows, macOS, Linux build candidates and an SBOM. These results establish CI **buildability and automated test portability**, not installer usability on clean machines, signed distribution, actual physical DGX Spark connectivity or independent penetration testing. The workflow source does not contain macOS notarization/Windows Authenticode signing. Subsequent documentation-only commits trigger additional runs and do not change this feature validation baseline.
