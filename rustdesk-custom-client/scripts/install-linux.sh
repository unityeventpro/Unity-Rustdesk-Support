#!/usr/bin/env bash
set -euo pipefail

DEB="$(dirname "$0")/UnityAVSupport-RustDesk.deb"
[[ -f "$DEB" ]] || { echo "Place UnityAVSupport-RustDesk.deb beside this script." >&2; exit 1; }
[[ -n "${UNITY_SUPPORT_PASSWORD:-}" ]] || { echo 'Set UNITY_SUPPORT_PASSWORD in this shell before installing.' >&2; exit 1; }
sudo apt-get install -y "$DEB"
rustdesk --password "$UNITY_SUPPORT_PASSWORD"
echo 'Unity AV Support RustDesk is installed and unattended access is configured.'
