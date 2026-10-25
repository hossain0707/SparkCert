#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PACKAGE="SparkCert-Linux-Ubuntu-x64"
mkdir -p dist/release
PKG_ROOT="$(mktemp -d)"
trap 'rm -rf "$PKG_ROOT"' EXIT
mkdir -p "$PKG_ROOT/opt/sparkcert" "$PKG_ROOT/usr/bin" "$PKG_ROOT/usr/share/applications" "$PKG_ROOT/usr/share/icons/hicolor/256x256/apps" "$PKG_ROOT/DEBIAN"
cp -a dist/SparkCert/. "$PKG_ROOT/opt/sparkcert/"
install -m 644 assets/sparkcert-icon.png "$PKG_ROOT/usr/share/icons/hicolor/256x256/apps/sparkcert.png"
cat > "$PKG_ROOT/usr/bin/sparkcert" <<'EOF'
#!/bin/sh
exec /opt/sparkcert/SparkCert "$@"
EOF
chmod +x "$PKG_ROOT/usr/bin/sparkcert"
cat > "$PKG_ROOT/usr/share/applications/sparkcert.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SparkCert
Comment=Local-first AI readiness workbench
Exec=/usr/bin/sparkcert
Icon=sparkcert
Terminal=false
Categories=Development;Utility;
StartupNotify=true
EOF
cat > "$PKG_ROOT/DEBIAN/control" <<'EOF'
Package: sparkcert
Version: 0.2.1~preview1
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Md Najmul Hossain
Depends: openssh-client, libgtk-3-0, libwebkit2gtk-4.1-0, gir1.2-webkit2-4.1
Description: SparkCert private AI readiness workbench (development preview)
 Local-first GUI for SSH-managed AI infrastructure diagnostics,
 model API evaluation, and evidence-based assessment reports.
 Unsigned preview; operator validation and acceptance are required.
Homepage: https://github.com/hossain0707/SparkCert
EOF
chmod -R a+rX "$PKG_ROOT/opt/sparkcert"
dpkg-deb --build --root-owner-group "$PKG_ROOT" "dist/release/${PACKAGE}.deb"
# Portable Linux archive: includes everything except external OpenSSH/GTK system libraries.
cp assets/sparkcert-icon.png dist/SparkCert/sparkcert-icon.png
cat > dist/SparkCert/START-HERE.txt <<'EOF'
SparkCert Linux x64 portable development preview

Requires Ubuntu 24.04 or compatible system with OpenSSH Client and GTK3/WebKitGTK 4.1.
Run ./SparkCert from this directory (do not move the executable out of its folder).
No cloud account is required. Import your existing SSH config aliases in Connections.
This package is not signed or validated on physical DGX Spark hardware.
EOF
tar -C dist -czf "dist/release/SparkCert-Portable-Linux-x64.tar.gz" SparkCert
printf 'Created Linux deb and portable tar.gz\n'
