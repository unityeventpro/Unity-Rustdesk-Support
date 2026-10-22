#!/usr/bin/env bash
set -euo pipefail

DEB="$(cd "$(dirname "$0")" && pwd)/UnityAVSupport-RustDesk.deb"
[[ -f "$DEB" ]] || { echo "Place UnityAVSupport-RustDesk.deb beside this script." >&2; exit 1; }
[[ -n "${UNITY_SUPPORT_PASSWORD:-}" ]] || { echo 'Set UNITY_SUPPORT_PASSWORD in this shell before installing.' >&2; exit 1; }
sudo apt-get install -y "$DEB"
sudo rustdesk --password "$UNITY_SUPPORT_PASSWORD"
echo 'Unity AV Support RustDesk is installed and unattended access is configured.'
