> **Current implementation differs from initial design:** v0.2 source has basic SSH tunnel management, guarded uploads/downloads and evidence controls. See `docs/PROJECT_STATUS.md` before interpreting any planned features below.

# SparkCert product requirements and complete feature vision

**Owner:** Md Najmul Hossain · **Product category:** local-first enterprise AI production-readiness assessment software · **Target:** NVIDIA DGX Spark first, SSH-managed Linux AI hosts second · **Snapshot:** 2026-10-25.

This file preserves the original product vision independently of how much of it has been implemented. For *actual delivery status*, read `PROJECT_STATUS.md`; never mistake this document for finished functionality.

## Positioning

**One-sentence value proposition:** a Windows/macOS/Linux application that can connect to one or more DGX Spark systems, run verifiable infrastructure and model checks, collect trustworthy evidence, and prepare clear reports that help engineers decide whether an AI service is ready for wider deployment.

**Important:** a readiness assessment is a decision-support tool, not official NVIDIA, ISO, medical, legal, regulatory, or independent accredited certification. The commercial name SparkCert is tentative and should be trademark-checked before sale. NVIDIA marks remain property of NVIDIA. NVIDIA Sync and DGX management functions already exist; differentiation must be **assessment methodology + evidence + reproducibility + private local workflow**.

## Intended users and primary jobs

| Persona | Job-to-be-done | Main successful outcome |
| --- | --- | --- |
| Solo LLM engineer | Connect without repeating VS Code SSH setup, diagnose and assess inference endpoint | Repeatable device + model checks and downloadable run evidence |
| IT administrator | Connect over Ethernet, LAN or VPN; diagnose a group of hosts | Clearly distinguish reachable/healthy/unverified/failed devices and causes |
| Enterprise AI lead | Compare deployed versions/models against release policy | Evidence-backed go/no-go decisions, not arbitrary green scores |
| AI researcher | Validate experiment/model behavior over time | Versioned baselines and reproducible results, later scientific-grade metrics |
| External consultant | Deploy private assessment workflow at client site | On-prem execution, client-owned data, branded/readable reports |

## Planned user journeys and acceptance tests

### Journey A — zero-friction remote SSH (MVP implemented partially)

1. Install desktop app on Windows/macOS/Linux. **Pending native installer proof**.
2. Click **Add DGX Spark**. Choose (a) manual IP/hostname + username + optional SSH key path; (b) import existing `~/.ssh/config` alias like VS Code Remote SSH. **Both profile modes implemented**.
3. For direct Ethernet, check link, IP, route, and appropriate NIC. For LAN/VPN, check connectivity; assist without making unapproved network changes. **Network setup wizard planned**.
4. Verify target SSH fingerprint with a separate trusted source; reject mismatches. **Uses OpenSSH strict checking now; in-app fingerprint-guided UX planned**.
5. Authenticate via OS SSH agent/key, with native terminal/password login fallback. **Implemented**; no password storage.
6. Show successful diagnostics and save the profile. **Implemented, manual action**.
7. Open integrated remote terminal and remote file browser, with upload/download later. **Native terminal and read-only listing now; embedded terminal/transfers planned**.
8. Save multiple devices, reconnect without reentering metadata. **Implemented profiles; no background fleet monitoring**.

### Journey B — infrastructure and endpoint validation (MVP implemented partially)

1. Read system/GPU/memory/disk/runtime diagnostics over read-only SSH. **Implemented**.
2. Run transparent infrastructure prerequisites, record each input and check result. **Seven implemented heuristic checks**.
3. Select an already-running model service exposed on a user-chosen OpenAI-compatible endpoint; privately route it through a manual SSH tunnel when needed. **Live HTTP checks implemented, automatic tunnel planned**.
4. Evaluate instruction following, output format, canned refusal/canary and custom deterministic rules. **Implemented narrowly**.
5. Future: perform realistic prompt-injection, RAG grounding, hallucination on gold datasets, security leakage, load, concurrency, latency distribution, model regression and calibration tests. **Planned**.
6. Export PDF/HTML/JSON evidence bundle with model/runtime versions, timestamps, raw/check summaries and limitations. **PDF implemented; HTML/JSON bundle and content signing planned**.
7. Never imply success for a test that was not run. **Required invariant**.

### Journey C — enterprise fleet and remote agent (future)

- One management station controls multiple registered Sparks, grouping devices and assigning policy baselines.
- Optional least-privileged agent handles continuous telemetry, model inventory and controlled local GPU benchmarking.
- Secure tunnel manager supports private endpoints; no SSH public exposure by default.
- Controlled deployments and rollback require explicit user consent; no unattended root escalation.
- Audit logs, encrypted/retained evidence, policy packs and team roles are future enterprise features.

### Journey D — recovery and diagnostics (future)

- For bootable/reachable hosts, gather logs, configuration and backup manifests remotely.
- For unbootable/factory-reset cases, provide an **offline recovery guide** grounded in NVIDIA procedures; do not promise that cable + SSH can recover an unbootable host.
- Destructive operations, image flashing and remote reset must be separated into a safety-reviewed product module requiring physical/hardware test coverage, verified backup, explicit confirmation, rollback and restrictions.

## Connectivity models and user-facing copy

| Mode | Technical strategy | User expectation |
| --- | --- | --- |
| Direct Ethernet (RJ45) | Existing operating-system IP routing + system SSH | Works after compatible IP configuration and SSH setup; not plug-and-play on every OS |
| Same LAN / Wi-Fi | Existing reachable LAN IP/name + system SSH | No dependency on cloud login |
| Remote Internet | Private VPN such as Tailscale or WireGuard, plus system SSH | VPN setup outside current app; no public relay/service supplied |
| VS Code compatibility | Parse `~/.ssh/config` Host aliases; defer actual resolution to OpenSSH | Honor authorized IdentityFile, Include, ProxyJump, port and ssh-agent behavior |
| Credentials | OS-agent keys and native terminal; no DB password/token persistence | Avoid requiring repeated copy/paste of secrets into SparkCert |

## Project architecture and design baseline

- Operator-local frontend (existing dependency-free HTML/CSS/JS; optional pywebview).
- Operator-local FastAPI orchestration/controller, token-protected, 127.0.0.1 only.
- OS OpenSSH and optional VPN/private tunnel for remote Linux/DGX Spark diagnostics.
- Independent OpenAI-compatible HTTP evaluator (currently operator-side and synchronous).
- SQLite evidence store + PDF renderer (currently no encryption).
- Future optional DGX agent/job orchestration/tunnels/policy packs; **not installed today**.
- Product UI: high-end, technically credible, dark navy/teal look with small, purposeful microinteractions, animated flow diagrams, keyboard/a11y support, strict reduced-motion support, honest live status indicators.

See `ARCHITECTURE.md` and `DESIGN_SYSTEM.md` for engineering specifications, and `ARCHITECTURE.html` for the animated visual tour.

## Commercial strategy (unvalidated hypotheses)

- Initial distribution: local-first MVP, source accessible to authorized owner/teams; license remains undecided.
- Differentiate against generic Nvidia orchestration products through measured application quality, reproducibility, customizable organization policies, and private evaluation.
- Possible monetization after security validation: consulting deployments, per-seat or per-team enterprise subscriptions, policy packs, fleet control and support, not claims of official certification.
- Price ideas previously discussed (~USD $199–$999/month for organization plans) are **speculative**, not validated willingness-to-pay data, and should never appear as fixed product pricing before customer discovery.
- DGX Spark-only addressable market may be narrow; maintain host-agnostic SSH and model API abstractions from the beginning.

## Out-of-scope without separate approval and safety validation

Cloud telemetry or automatic uploading of client documents; exposing local controller on 0.0.0.0; storing private keys or API secrets in plaintext; bypassing SSH fingerprint checks; silent Docker/sudo installs; unattended factory reset; fabricated GPU metrics; official certification statements; user claims of NVIDIA partnership; auto-pushing to an owned GitHub repository without a requested repository destination.
