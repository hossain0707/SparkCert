# SparkCert · v0.2.1 development preview

> **Unsigned testing builds — not a production, certified, or NVIDIA-endorsed release.** Run them only on systems where you are authorized to install unverified development software. Follow your organization's security policies; do not disable endpoint security to install this preview.

SparkCert provides a local-first user interface for authenticated SSH diagnostics, private port forwarding to already-running model APIs, limited remote file transfers, model evaluations, and evidence-backed PDF reports.

## Pick your download

| Operating system | Download asset | Install |
| --- | --- | --- |
| Windows 10/11 x64 | `SparkCert-Setup-Windows-x64.exe` | Run the per-user setup and use the Start Menu shortcut. |
| Windows 10/11 x64 (portable) | `SparkCert-Portable-Windows-x64.zip` | Extract the **entire** archive and run `SparkCert.exe` inside the `SparkCert` folder. |
| macOS Apple silicon | `SparkCert-macOS-Apple-Silicon.dmg` | Open DMG and drag `SparkCert.app` to Applications. |
| macOS Intel | `SparkCert-macOS-Intel.dmg` | Open DMG and drag `SparkCert.app` to Applications. |
| Ubuntu 24.04 x64 | `SparkCert-Linux-Ubuntu-x64.deb` | Install via Ubuntu Software or `sudo apt install ./SparkCert-Linux-Ubuntu-x64.deb`. |
| Linux x64 (portable) | `SparkCert-Portable-Linux-x64.tar.gz` | Extract and run `SparkCert/SparkCert`; supply GTK3/WebKitGTK 4.1 and `ssh`. |

Check the `SHA256SUMS.txt` asset after downloading. GitHub release file checksums verify transfer integrity; they are **not** code signing.

**If Windows SmartScreen or macOS Gatekeeper blocks installation, don't bypass institutional security policies.** For a controlled personal testing device, prefer running the open-source/source-readable Python app until a signed release is available. Unverified binaries can be rejected by OS security.

## First-use checklist

1. Install or verify the system OpenSSH client (`ssh -V`).
2. Ensure your DGX Spark is reachable by LAN/Ethernet or a separately configured secure VPN.
3. Verify your DGX Spark SSH host key using a trusted channel; do not accept unknown fingerprints blindly.
4. Import an existing `~/.ssh/config` alias or manually enter host, port, username, and existing key reference.
5. Run **Diagnostics**, then use **Private tunnel** for a model API that is already running.
6. Run AI evaluations against the tunneled localhost API and export evidence reports.

No NVIDIA approved certification is issued. The app does not provision a DGX Spark, install AI models automatically, install remote agents, or recover an unbootable device. Real DGX Spark validation, accessibility acceptance, pen-testing and signing/notarization remain pending.

For full details and troubleshooting: [Installation & connectivity](https://github.com/hossain0707/SparkCert/blob/main/docs/INSTALLATION.md), [Release checklist](https://github.com/hossain0707/SparkCert/blob/main/docs/RELEASE_CHECKLIST.md), and [Project handover](https://github.com/hossain0707/SparkCert/blob/main/docs/WORKSPACE_HANDOFF.md).
