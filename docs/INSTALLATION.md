# Install SparkCert on Windows, macOS and Linux

**Release track:** v0.2.1 developer preview · **Status:** unsigned, not production-qualified or accredited.

This guide applies to the package artifacts built by `.github/workflows/ci.yml`. Those packages are intended for controlled testing only until clean-computer acceptance and signing are completed.

## Download verified preview artifacts

1. Open [GitHub Releases](https://github.com/hossain0707/SparkCert/releases).
2. Select the most recent **SparkCert developer preview**, not the source-code archive.
3. Expand **Assets** and choose the asset for your computer architecture.
4. Optionally validate it against `SHA256SUMS.txt`. SHA-256 is an integrity check, not a code signature.
5. Follow the operating system steps below. Do not turn off your company's OS security policies.

| OS | Asset | Install / start | Host requirements |
| --- | --- | --- | --- |
| Windows x64 | `SparkCert-Setup-Windows-x64.exe` | Per-user install; launch via Start menu | Windows 10/11, Microsoft Edge WebView2 runtime, OpenSSH Client |
| Windows x64 portable | `SparkCert-Portable-Windows-x64.zip` | Extract entire `SparkCert/` folder then run `SparkCert.exe` | Same as above |
| macOS Apple silicon | `SparkCert-macOS-Apple-Silicon.dmg` | Drag `SparkCert.app` into Applications | macOS 15 or newer recommended, OpenSSH |
| macOS Intel | `SparkCert-macOS-Intel.dmg` | Drag `SparkCert.app` into Applications | macOS 15 or newer recommended, OpenSSH |
| Ubuntu 24.04 x64 | `SparkCert-Linux-Ubuntu-x64.deb` | Software Center or `sudo apt install ./SparkCert-Linux-Ubuntu-x64.deb` | OpenSSH, GTK3/WebKitGTK 4.1 |
| Linux x64 portable | `SparkCert-Portable-Linux-x64.tar.gz` | Extract folder; run `./SparkCert` within it | OpenSSH, compatible Linux GTK3/WebKitGTK 4.1 |

For any package, a lack of a visible Release asset means the **automated release pipeline has not successfully built that package**. Do not represent an uploaded source archive or the CI badge as an installer.

## Windows 10 and 11

1. Verify built-in OpenSSH Client in **Settings → Optional Features** or run `ssh -V` from PowerShell.
2. Verify **Microsoft Edge WebView2 Runtime** is installed (normally present in current Windows 10/11). The GUI requires it.
3. Run the unsigned development setup on a personally authorized testing PC, or extract the portable ZIP to a writable folder.
4. Use the **SparkCert** Start Menu entry or run `SparkCert.exe` from the extracted complete directory.
5. For a real Spark connection, test `ssh my-dgx-spark` in PowerShell first; then import that alias inside SparkCert.

**Unsigned app warnings:** An unsigned build may be blocked by SmartScreen or company endpoint security. Do not bypass security policy. Request an officially signed build for managed workstations.

## macOS Apple silicon and Intel

1. Choose the **correct architecture**; Apple silicon is M1/M2/M3/M4/M5 series, Intel uses the Intel download.
2. Open DMG and drag the app to **Applications**.
3. Ensure your SSH alias/key already works in Terminal with `ssh my-dgx-spark`.
4. Run the app from Applications and import the host profile.

**Unsigned/not-notarized:** Gatekeeper may block the developer preview. Do not disable Gatekeeper or other corporate controls. Source mode is the reviewable alternative while developer signing/notarization are pending.

## Ubuntu 24.04 x64

```bash
sudo apt install ./SparkCert-Linux-Ubuntu-x64.deb
sparkcert
```

For the portable `.tar.gz` download:

```bash
tar -xzf SparkCert-Portable-Linux-x64.tar.gz
cd SparkCert
./SparkCert
```

The desktop GUI uses GTK3 and WebKitGTK 4.1. The `.deb` declares required dependencies and installs a desktop application entry. On other distributions, install equivalent shared libraries and OpenSSH with the system package manager. The portable Linux build is not an AppImage and is not distro-universal.

## Connect to DGX Spark

1. Ensure Spark is already configured and powered on. SparkCert does not automatically set up IP networking or create device accounts.
2. Link directly by Ethernet, join the same network, or use an existing private VPN. A direct link may require compatible static IP addresses.
3. Independently verify the device's SSH server fingerprint using your device console/administrator and let OpenSSH record it into `known_hosts`.
4. Set up key-based SSH + agent for background diagnostics; password sessions can be opened in your OS terminal.
5. Import the same `~/.ssh/config` alias you use in VS Code Remote-SSH, or enter hostname, port, username and private key reference manually.
6. Run the read-only **Diagnostics** action. Then optionally open a local-only model API tunnel.

SSH keys and passwords should remain in the OS/SSH agent; never upload private key material into GitHub or repository issues.

## Common issues

| Symptom | Explanation / next step |
| --- | --- |
| App window does not start | Check WebView2 on Windows or GTK/WebKitGTK on Linux. Read CI package-check report for build-level import failures. |
| Connection timeout | Check the host IP, cabling, VPN, firewall and that port 22 is reachable. |
| Host key verification failed | Re-verify the new fingerprint through a trusted administrator. Do not disable `StrictHostKeyChecking`. |
| Diagnostics say authentication failed | Unlock your SSH agent or configure an authorized key for unattended commands. |
| Model endpoint unreachable | The model server must already be running. Tunnel only forwards a port; it does not deploy/launch a model. |
| macOS/Windows flags unsigned app | This is a preview without notarization/signature. Follow OS/enterprise policy; use source instead if blocked. |
| Report content is sensitive | Evaluation prompts/responses are stored in local SQLite unless deleted by your retention controls. Do not test secrets or patient data without organizational approval. |

For security boundaries, see [SECURITY_MODEL.md](SECURITY_MODEL.md); for release gates, see [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
