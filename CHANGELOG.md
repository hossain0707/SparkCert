# SparkCert changelog

## 0.2.0 — 2026-10-25 (development candidate, NOT production-certified)

### Added
- Operator-controlled SSH port forwards bound to localhost, with lifecycle shutdown and active tunnel management.
- Bounded SSH file upload/download using a fixed remote Python3 helper and home-directory confinement checks. Uploads are uniquely named in `~/sparkcert-uploads`.
- Configurable 1–3 model-test repetitions and 1–4 concurrent client requests; measured p50/p95 latency in evidence reports.
- Local audit event history, selective report deletion and 1–3650 day retention purge.
- SHA-256 checksum of new stored result JSON with explicit status; PDF export refused if checksum no longer matches.
- Cross-platform CI test matrix, unsigned build candidates, dependency audit/SBOM workflow definitions and six additional tests.
- Refined responsive UI sections and mock-only browser smoke tests for desktop/mobile.

### Compatibility / breaking-change notes
- Existing SQLite histories migrate automatically with a nullable `result_sha256`; legacy records are labeled `legacy_unverified` and are not retroactively attested.
- The offline UI screenshot is not a live real-device demo. `OpenSSH` and remote `python3` are required for tunnel/transfer features.
- No paid cloud services, background workers, unsupported reset methods or automatic installation of remote agents were added.

### Known release blockers
- No physically verified DGX Spark/Windows/macOS end-to-end results, signed installers, external security audit or calibrated certification process. v0.2.0 is a development candidate only.

## 0.1.0 — 2026-10-25 (initial MVP)

- Local FastAPI UI, SSH profile management, read-only host probes, four model behavior checks, SQLite and PDF evidence, source-based desktop packaging recipes, initial professional architecture and handover documentation.
