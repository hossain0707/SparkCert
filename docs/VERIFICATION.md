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
