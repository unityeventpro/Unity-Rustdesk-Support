#!/bin/bash
set -euo pipefail

DMG="$(dirname "$0")/UnityAVSupport-RustDesk.dmg"
APP_NAME="RustDesk"
MOUNT="$(mktemp -d /tmp/unity-rustdesk.XXXXXX)"
cleanup() { hdiutil detach "$MOUNT" -quiet >/dev/null 2>&1 || true; rmdir "$MOUNT" 2>/dev/null || true; }
trap cleanup EXIT

[[ -n "${UNITY_SUPPORT_PASSWORD:-}" ]] || { echo "Set UNITY_SUPPORT_PASSWORD in this shell before installing." >&2; exit 1; }
[[ -f "$DMG" ]] || { echo "Place UnityAVSupport-RustDesk.dmg beside this script." >&2; exit 1; }
hdiutil attach "$DMG" -readonly -nobrowse -mountpoint "$MOUNT" -quiet
[[ -d "$MOUNT/$APP_NAME.app" ]] || { echo "Expected $APP_NAME.app inside the disk image." >&2; exit 1; }
sudo ditto "$MOUNT/$APP_NAME.app" "/Applications/$APP_NAME.app"
"/Applications/$APP_NAME.app/Contents/MacOS/$APP_NAME" --password "$UNITY_SUPPORT_PASSWORD"
echo 'Unity AV Support RustDesk is installed and unattended access is configured.'
