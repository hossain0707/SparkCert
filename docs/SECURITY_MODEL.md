# SparkCert — v0.2 security model and residual risks

**Architecture:** locally served FastAPI controller on loopback; system OpenSSH for host access and private tunnels; direct HTTP(S) to a user-selected already-running model API; SQLite/PDF local storage. User's operating system account is the local trust boundary.

## Assets

- SSH host configuration, private key *paths* and local ssh-agent; SparkCert never reads private key bytes into its database.
- Operator's remote files and permission-limited uploaded artifacts.
- Confidential model evaluation prompts, model outputs and exported PDF reports.
- Local assessment history and execution metadata.

## Implemented controls

- Loopback-only server, per-launch API token, CSP, origin/host checks, escaped UI rendering.
- System OpenSSH enforces strict known-host verification, ssh-agent and existing SSH configuration; `BatchMode` for automated probes.
- Fixed, reviewed remote diagnostic helper commands; no user-supplied general remote shell command endpoint.
- SSH port forwards listen on `127.0.0.1`, close at user request/app shutdown, maximum four active.
- Remote file transfers require consent, are limited to 16 MiB, and use a fixed Python3 helper with base64-decoded data parameters. Remote uploads use `~/sparkcert-uploads` with private directory permissions and exclusive unique filenames.
- Evaluation requests have bounded cases, repetitions, concurrency and model response body size; redirects are disabled and `trust_env=False` for HTTPX.
- API keys are request-only; private SSH keys/passwords are not stored; the app records local non-content audit events.
- Result SHA-256 detects simple accidental DB alterations; altered records are blocked from PDF export. This is not independently attested.

## Residual risks preventing production certification

1. **Local adversary:** another process under the same operating system user, or malicious local processes able to access loopback, can fetch the HTML session token. The token protects against casual cross-origin browser operations, not hostile same-host processes. Production deployments must rely on OS account isolation / secure IPC or a stronger authentication boundary.
2. **Unencrypted at-rest data:** SQLite and PDFs can contain sensitive model outputs. The default storage is **not encrypted**. Do not enter patient identifiers, credentials or legally protected information without an approved data policy.
3. **Remote helper trust:** file operations are constrained by remote Python3 validation but a hostile account with concurrent permission to modify target directories may race symlinks/path resolution. Dedicated low-privilege accounts or hardened SFTP policies may be required for enterprise use.
4. **Network destination trust:** the user-selected OpenAI-compatible HTTP endpoint receives test prompts. Prefer a verified localhost SSH tunnel/private VPN and TLS where applicable. An intentional external URL may export confidential prompts.
5. **Resource exhaustion:** repeated long running model tests or large file multipart uploads can consume host resources. Bounded per-action sizes exist, but rate limiting/cancelable jobs and process isolation need more work.
6. **Evidence integrity:** a privileged attacker can change both stored JSON and its SHA-256 digest. Cryptographically signed evidence packs, immutable storage and verified timestamps are future items.
7. **Distribution:** build artifacts are unsigned. There is no verified auto-update, signature verification or release rollback mechanism yet.
8. **Dependency review:** CI pip-audit succeeds as of run 40145092403; this is not a penetration test, supply-chain review or safety certification.
9. **Actual NVIDIA DGX Spark:** no real hardware session has been executed in this workspace; driver/OS-specific failures may exist.

## Next security reviews

- Independent review of host-key error paths, SSH command encoding and remote-transfer race conditions.
- Local browser token origin/CSRF/host-header threat modeling; rate limits and job isolation.
- Encryption/keychain architecture with safe backups, retention and PII redaction.
- Version-pinned software bill of materials, signed releases, CI artifact provenance and penetration testing.

This document records architectural analysis, not an independent vulnerability assessment.
