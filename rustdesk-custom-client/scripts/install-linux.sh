#!/usr/bin/env bash
set -euo pipefail

DEB="$(cd "$(dirname "$0")" && pwd)/UnityAVSupport-Linux-amd64.deb"
[[ -f "$DEB" ]] || { echo "Place UnityAVSupport-Linux-amd64.deb beside this script." >&2; exit 1; }
sudo apt-get install -y "$DEB"
if [[ -n "${UNITY_SUPPORT_PASSWORD:-}" ]]; then
  sudo rustdesk --password "$UNITY_SUPPORT_PASSWORD"
fi
echo 'Unity AV Support RustDesk is installed.'
