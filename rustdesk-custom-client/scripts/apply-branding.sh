#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/rustdesk-source" >&2
  exit 2
fi

SOURCE_DIR="$(cd "$1" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGO="$SCRIPT_DIR/../brand/unity-av-support-logo.png"
CONFIG="$SOURCE_DIR/libs/hbb_common/src/config.rs"
GITIGNORE="$SOURCE_DIR/.gitignore"

[[ -f "$LOGO" ]] || { echo "Missing logo: $LOGO" >&2; exit 1; }
[[ -f "$CONFIG" ]] || { echo "Not a RustDesk source tree: $SOURCE_DIR" >&2; exit 1; }
[[ -f "$GITIGNORE" ]] || { echo "Missing RustDesk .gitignore: $GITIGNORE" >&2; exit 1; }

python3 - "$CONFIG" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old_server = 'pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];'
new_server = 'pub const RENDEZVOUS_SERVERS: &[&str] = &["codehalter.does-it.net"];'
old_key = 'pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";'
new_key = 'pub const RS_PUB_KEY: &str = "Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM=";'

for old, new, label in ((old_server, new_server, "server"), (old_key, new_key, "key")):
    if old in text:
        text = text.replace(old, new)
    elif new not in text:
        raise SystemExit(f"Could not find expected RustDesk {label} constant; no source written")

path.write_text(text, encoding="utf-8")
PY

python3 - "$GITIGNORE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
exceptions = "\n# Keep Unity AV Support client artwork in source releases.\n!flutter/assets/icon.png\n!flutter/assets/logo.png\n!flutter/assets/logo_light.png\n!flutter/assets/logo_dark.png\n"
if "!flutter/assets/icon.png" not in text:
    marker = "*png\n"
    if marker not in text:
        raise SystemExit("Could not find the expected PNG ignore rule; no .gitignore written")
    path.write_text(text.replace(marker, marker + exceptions, 1), encoding="utf-8")
PY

ASSETS="$SOURCE_DIR/flutter/assets"
mkdir -p "$ASSETS"
install -m 0644 "$LOGO" "$ASSETS/icon.png"
install -m 0644 "$LOGO" "$ASSETS/logo.png"
install -m 0644 "$LOGO" "$ASSETS/logo_light.png"
install -m 0644 "$LOGO" "$ASSETS/logo_dark.png"
install -m 0644 "$LOGO" "$SOURCE_DIR/res/icon.png"
install -m 0644 "$LOGO" "$SOURCE_DIR/res/mac-icon.png"

echo "Applied Unity AV Support assets and self-hosted server defaults to: $SOURCE_DIR"
echo "Before building, run 'flutter pub get' and 'flutter pub run flutter_launcher_icons' from the flutter directory."
echo "Build this source on each target platform using RustDesk's official Flutter build guide."
