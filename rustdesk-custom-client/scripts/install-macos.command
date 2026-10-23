#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
shopt -s nullglob
PACKAGES=("$DIR"/UnityAVSupport-macOS-*.pkg)
[[ ${#PACKAGES[@]} -eq 1 ]] || { echo 'Keep exactly one matching Mac package beside this helper.' >&2; exit 1; }
sudo /usr/sbin/installer -pkg "${PACKAGES[0]}" -target /
if [[ -n "${UNITY_SUPPORT_PASSWORD:-}" ]]; then
  sudo /Applications/RustDesk.app/Contents/MacOS/RustDesk --password "$UNITY_SUPPORT_PASSWORD"
fi
echo 'Unity AV Support RustDesk is installed in /Applications.'
