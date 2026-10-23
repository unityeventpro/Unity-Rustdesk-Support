#!/usr/bin/env python3
"""Check the compiled payload and both EXE icons before publishing a Windows build."""
import hashlib
import json
import struct
from pathlib import Path

root = Path('.')
dll = (root / 'rustdesk/librustdesk.dll').read_bytes()
config_source = (root / 'libs/hbb_common/src/config.rs').read_text()
for key, value in {
    'custom-rendezvous-server': 'codehalter.does-it.net',
    'relay-server': 'codehalter.does-it.net:21117',
    'api-server': 'https://support.unityavs.com',
    'key': 'Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM=',
}.items():
    assert f'settings.insert("{key}".to_owned(), "{value}".to_owned());' in config_source

for expected in (b'codehalter.does-it.net', b'codehalter.does-it.net:21117',
                 b'https://support.unityavs.com', b'Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM=',
                 b'Unity AVS Support.lnk'):
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
assert manifest['id_server'] == 'codehalter.does-it.net'
assert manifest['relay_server'] == 'codehalter.does-it.net:21117'
assert manifest['public_key'] == 'Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM='
assert manifest['api_server'] == 'https://support.unityavs.com'
assert manifest['desktop_shortcut_label'] == 'Unity AVS Support'
for path in (root / 'rustdesk/rustdesk.exe', root / 'unity-dist' / manifest['installer_file']):
    binary = path.read_bytes()
    pe = struct.unpack_from('<I', binary, 60)[0]
    assert binary[:2] == b'MZ' and binary[pe:pe + 4] == b'PE\0\0'
    assert struct.unpack_from('<H', binary, pe + 4)[0] == 0x8664
    assert largest in binary, f'Generated launcher icon is missing from {path}'
    print(path, hashlib.sha256(binary).hexdigest())
print('Verified compiled ID/relay/API servers, public key, desktop label, x64 EXEs and matching launcher icon resources.')
