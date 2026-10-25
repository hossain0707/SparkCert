# SparkCert — Windows, macOS and Linux onboarding

**Audience:** developers and operators testing the v0.2.0 development candidate; **not** a supported public production release.

## Prerequisites

- Python 3.11+, system OpenSSH client, browser. Optional desktop window requires `pywebview` with platform-native webview libraries.
- SSH account on DGX Spark/Linux target, trusted network route (direct Ethernet, LAN/Wi-Fi, or a separately configured private VPN), known SSH host key verified out of band.
- Remote `python3` for bounded upload/download; `nvidia-smi`/Docker for relevant readiness checks; an **already running** OpenAI-compatible LLM endpoint for evaluation.

## Run from source

```sh
git clone https://github.com/hossain0707/SparkCert.git
cd SparkCert
python -m venv .venv
# macOS and Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m sparkcert
```

On Windows install Microsoft OpenSSH Client from **Settings → Optional features** if `ssh -V` fails. On macOS and Linux use the built-in or distribution OpenSSH client. The app only binds `127.0.0.1` and opens your browser.

Optional native wrapper:

```sh
python -m pip install -e '.[desktop]'
python -m sparkcert.__main_desktop__
```

## Connection flow

1. Make DGX Spark reachable (e.g. via a verified IP or alias). A directly connected Ethernet cable may need a static/assigned compatible IPv4 address on both ends.
2. In a **trusted terminal**, verify the SSH server host fingerprint. Do not disable strict host-key checks.
3. Confirm `ssh my-dgx-spark` (or `ssh your-user@device-address`) works; set up an SSH agent/key for noninteractive diagnostics.
4. In SparkCert choose **Connections → Manual** or **SSH config import**, save, then run **Diagnostics**. A saved profile alone is not proof of a successful connection.
5. If a compatible model API is running on the host's `127.0.0.1:8000`, choose **Private model API tunnel**, set remote port `8000` and auto local port `0`. Use the returned localhost endpoint on the evaluation page.
6. File downloads are home-scoped; uploads (if explicitly approved) go into `~/sparkcert-uploads` with unique names; each transfer is max 16 MiB.
7. Export PDF only after executing actual checks. Use **Settings & Security** for local retention and audit controls.

## Packaging and limitations

The GitHub [CI run 40145092403](https://github.com/hossain0707/SparkCert/actions/runs/40145092403) produced unsigned Windows/macOS/Linux **build candidates**. For controlled development testing, visit the run's Artifacts section while logged into GitHub. Installing unsigned macOS/Windows software may trigger platform warnings. Do not recommend bypassing endpoint security policies for commercial or organizational use.

The app does not automatically configure IP networking, start model servers, install remote agents, restore unbootable devices, issue official certificates or protect stored model outputs with disk encryption. Hardware validation and signed installers remain outstanding. See [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).
