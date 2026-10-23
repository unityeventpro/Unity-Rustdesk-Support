#!/usr/bin/env bash
# Build a native Installer package that always installs in /Applications.
set -euo pipefail
APP="${1:?Usage: package-macos.sh APP VERSION OUTPUT.pkg}"
VERSION="${2:?Missing version}"
OUTPUT="${3:?Missing output path}"
[[ -d "$APP/Contents" ]] || { echo 'App bundle not found' >&2; exit 1; }
codesign --verify --deep --strict "$APP"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/root/Applications"
ditto "$APP" "$STAGE/root/Applications/RustDesk.app"
pkgbuild --analyze --root "$STAGE/root" "$STAGE/components.plist"
python3 - "$STAGE/components.plist" <<'PY'
import plistlib, sys
path = sys.argv[1]
with open(path, 'rb') as f:
    components = plistlib.load(f)
for component in components:
    component['BundleIsRelocatable'] = False
    component['BundleHasStrictIdentifier'] = True
    component['BundleOverwriteAction'] = 'upgrade'
with open(path, 'wb') as f:
    plistlib.dump(components, f)
PY
pkgbuild --root "$STAGE/root" --component-plist "$STAGE/components.plist" \
  --identifier com.unityeventpro.rustdesk --version "$VERSION" \
  --install-location / --ownership recommended "$OUTPUT"
