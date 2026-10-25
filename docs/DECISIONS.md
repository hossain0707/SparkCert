# SparkCert architecture decision record (ADR)

Every future material decision should be added as an immutable dated ADR, describing context, options, consequences and test requirements.

## ADR-001 · 2026-10-25 · Local-only client controller (accepted)

**Choice:** FastAPI runs on operator computer on `127.0.0.1`, started by CLI/browser or optional pywebview native window. No cloud sign-in or hosted controller required.

**Reason:** private/air-gapped enterprise environments; easy iteration; minimal operating cost; cross-platform development.

**Trade-off:** no team/multi-user RBAC, no cloud orchestration, native builds need OS-specific distribution tests and signing.

## ADR-002 · 2026-10-25 · Use system OpenSSH (accepted)

**Choice:** parse aliases but delegate actual SSH protocol/key handling to installed OpenSSH, respecting `known_hosts`, `ssh-agent`, `IdentityFile`, `Include`, `ProxyJump`.

**Reason:** matches VS Code Remote SSH workflows, avoids unsafe private key handling and complex SSH library duplication.

**Trade-off:** must provide clear OS prerequisites, key-agent UX, first-connection host verification; password-only background commands unavailable.

## ADR-003 · 2026-10-25 · Evidence first, marketing claims second (accepted)

**Choice:** reports contain only executed checks; pass percentage reflects sample check set and known limitations; product independent of NVIDIA accreditation.

**Reason:** engineering credibility, reproducibility, customer trust; avoids false certification/safety claims.

**Trade-off:** a small initial suite cannot establish full production readiness; deeper evaluation requires datasets, policy, benchmarks and independent methodology.

## ADR-004 · 2026-10-25 · No installed remote agent in MVP (accepted)

**Choice:** pre-defined read-only SSH commands and direct OpenAI-compatible API calls; no remote root agent or automatic model installation.

**Reason:** reduce attack surface and get basic evaluation and reporting functional sooner.

**Trade-off:** no continuous telemetry, job queues, server-side benchmarks or automatic private tunnel creation.

## ADR-005 · 2026-10-25 · Design motion communicates structure, not device state (accepted)

**Choice:** animated page transitions/hover/data-flow diagrams; labels explain that flow lines are conceptual; reduced-motion support.

**Reason:** user explicitly requests sophisticated and animated software, but fake activity would undermine evidence trust.

**Trade-off:** animation must be performance-tested, keep focus visible, and be disabled for motion-sensitive users.

## ADR-006 · 2026-10-25 · Source portability through self-contained handoff (accepted)

**Choice:** ship documentation, local HTML architecture view, status matrix, tests, continuation prompt, source archive and checksums together. Keep platform-specific SSH keys/database outside ZIP.

**Reason:** development must continue from any new workspace without losing architecture/design/feature history.

**Trade-off:** archive is only a versioned snapshot; Git-based commits/synchronization remain a separate owner action.

## ADR-007 · 2026-10-25 · Process-local private SSH tunnels (accepted for v0.2 dev)

Expose opt-in OpenSSH port forwards bound to `127.0.0.1`, using strict known-host checking and existing aliases/key-agent configuration. Limit to four concurrent processes, close on request/device deletion/app exit, and avoid saving active processes as permanent settings. A listening forward is **not** an API health guarantee. Network errors and physical VPN tests remain outstanding.

## ADR-008 · 2026-10-25 · Bound optional transfers rather than broad remote filesystem writes (accepted for v0.2 dev)

Retain read-only file browsing. For explicit operator uploads, use a fixed remote Python3 helper and unique file names under `~/sparkcert-uploads` with restrictive permissions. Downloads are home-scoped; both directions limited to 16 MiB. Inputs are base64-encoded as data to fixed remote scripts; never use raw user shell syntax. Remote untrusted-filesystem races and real-device validation remain open. No arbitrary remote reset or model installer.

## ADR-009 · 2026-10-25 · Measured latency and local evidence integrity (accepted for v0.2 dev)

Provide bounded 1–3 repetitions and 1–4 concurrent model requests with observed p50/p95 latency; score per defined test case only. Save SHA-256 of serialized evidence, block PDF export if the saved checksum mismatches and allow explicit retention purges with content-free local audit events. Digest is not independent attestation, storage is not encrypted, and benchmarks remain exploratory.
