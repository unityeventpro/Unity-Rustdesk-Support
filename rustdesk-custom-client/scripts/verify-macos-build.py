#!/usr/bin/env python3
"""Verify the compiled Mac payload before local Developer ID signing."""
import hashlib
import json
import runpy
import struct
import sys
from pathlib import Path

arch = sys.argv[1]
app = Path('flutter/build/macos/Build/Products/Release/RustDesk.app')
lib = (app / 'Contents/Frameworks/liblibrustdesk.dylib').read_bytes()
preset = runpy.run_path(str(Path(__file__).with_name('validate-preset-password.py')))['load_preset']()
for value in ['codehalter.does-it.net', 'codehalter.does-it.net:21117',
              'https://support.unityavs.com',
              'Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM=',
              'use-permanent-password', *preset.values()]:
    assert value.encode() in lib, 'Compiled Mac client is missing required configuration'
for path in [app / 'Contents/MacOS/RustDesk', app / 'Contents/MacOS/service',
             app / 'Contents/Frameworks/liblibrustdesk.dylib']:
    b = path.read_bytes()
    assert b[:4] == b'\xcf\xfa\xed\xfe', f'Expected thin 64-bit Mach-O: {path.name}'
    assert struct.unpack_from('<I', b, 4)[0] == {'aarch64': 0x0100000c, 'x86_64': 0x01000007}[arch]
assert (app / 'Contents/Resources/AppIcon.icns').stat().st_size > 0
launcher = Path('.unity-kit/rustdesk-custom-client/brand/unity-avs-launcher-icon.png').read_bytes()
assert Path('res/mac-icon.png').read_bytes() == launcher
asset = app / 'Contents/Frameworks/App.framework/Versions/A/Resources/flutter_assets/assets/icon.png'
if not asset.exists():
    matches = list(app.rglob('flutter_assets/assets/icon.png'))
    assert len(matches) == 1
    asset = matches[0]
assert asset.read_bytes() == launcher
manifest = json.loads(Path('unity-dist/build-info.json').read_text())
assert manifest['architecture'] == arch
assert manifest['api_server'] == 'https://support.unityavs.com'
assert manifest['relay_server'] == 'codehalter.does-it.net:21117'
assert manifest['authentication'] == 'permanent-password-only'
print('Verified Mac architecture, four server settings, permanent-password verifier/mode and launcher artwork.')
print('Launcher SHA256:', hashlib.sha256(launcher).hexdigest())
