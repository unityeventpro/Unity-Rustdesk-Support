#!/usr/bin/env python3
"""Check the compiled payload and both EXE icons before publishing a Windows build."""
import hashlib
import json
import struct
from pathlib import Path

root = Path('.')
dll = (root / 'rustdesk/librustdesk.dll').read_bytes()
for expected in (b'https://support.unityavs.com', b'Unity AVS Support.lnk'):
    if expected not in dll:
        raise SystemExit(f'Compiled client is missing {expected!r}')
ico = (root / 'flutter/windows/runner/resources/app_icon.ico').read_bytes()
reserved, kind, count = struct.unpack_from('<HHH', ico)
assert (reserved, kind) == (0, 1) and count > 0
images = []
for i in range(count):
    size, offset = struct.unpack_from('<II', ico, 6 + 16 * i + 8)
    images.append(ico[offset:offset + size])
largest = max(images, key=len)
manifest = json.loads((root / 'unity-dist/build-info.json').read_text())
assert manifest['api_server'] == 'https://support.unityavs.com'
assert manifest['desktop_shortcut_label'] == 'Unity AVS Support'
for path in (root / 'rustdesk/rustdesk.exe', root / 'unity-dist' / manifest['installer_file']):
    binary = path.read_bytes()
    pe = struct.unpack_from('<I', binary, 60)[0]
    assert binary[:2] == b'MZ' and binary[pe:pe + 4] == b'PE\0\0'
    assert struct.unpack_from('<H', binary, pe + 4)[0] == 0x8664
    assert largest in binary, f'Generated launcher icon is missing from {path}'
    print(path, hashlib.sha256(binary).hexdigest())
print('Verified compiled API URL, desktop label, x64 EXEs and matching launcher icon resources.')
