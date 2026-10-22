#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/rustdesk-source" >&2
  exit 2
fi

SOURCE_DIR="$(cd "$1" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/apply-branding.sh" "$SOURCE_DIR"

command -v flutter >/dev/null || { echo "Flutter is required; follow the official guide for this platform." >&2; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 is required." >&2; exit 1; }

(
  cd "$SOURCE_DIR/flutter"
  flutter pub get
  flutter pub run flutter_launcher_icons
)
cd "$SOURCE_DIR"
python3 build.py --flutter
