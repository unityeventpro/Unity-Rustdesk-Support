#!/usr/bin/env python3
"""Sign a copied app, package it, and notarize using credentials held in Keychain."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

MACHO = {b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf',
         b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'}
ENTITLEMENTS = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>com.apple.security.app-sandbox</key><false/>
<key>com.apple.security.cs.allow-jit</key><true/>
<key>com.apple.security.device.audio-input</key><true/>
<key>com.apple.security.network.client</key><true/>
</dict></plist>
'''


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('app', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--identity', required=True)
    parser.add_argument('--installer-identity', required=True)
    parser.add_argument('--notary-profile', required=True)
    parser.add_argument('--version', default='1.5.1')
    args = parser.parse_args()
    if not (args.app / 'Contents/MacOS/RustDesk').is_file():
        parser.error('Expected a complete RustDesk.app')
    output = args.output.resolve()
    if output.exists():
        parser.error('Output already exists; choose a new release output path')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='unity-sign-') as temp:
        temp = Path(temp)
        app = temp / 'RustDesk.app'
        run('ditto', args.app.resolve(), app)
        entitlements = temp / 'Release.entitlements'
        # Matches pinned upstream flutter/macos/Runner/Release.entitlements.
        entitlements.write_text(ENTITLEMENTS)
        # Sign code inside-out, preserving symlinks and avoiding --deep signing.
        for file in sorted(app.rglob('*')):
            if file.is_symlink() or not file.is_file():
                continue
            with file.open('rb') as stream:
                magic = stream.read(4)
            if magic in MACHO:
                run('codesign', '--force', '--sign', args.identity, '--timestamp',
                    '--options', 'runtime', file)
        bundles = [p for p in app.rglob('*') if p.is_dir() and not p.is_symlink()
                   and p.suffix in ('.framework', '.bundle', '.app')]
        for bundle in sorted(bundles, key=lambda p: len(p.parts), reverse=True):
            run('codesign', '--force', '--sign', args.identity, '--timestamp',
                '--options', 'runtime', bundle)
        run('codesign', '--force', '--sign', args.identity, '--timestamp',
            '--options', 'runtime', '--entitlements', entitlements, app)
        run('codesign', '--verify', '--deep', '--strict', '--verbose=2', app)
        unsigned = temp / 'unsigned.pkg'
        run('bash', Path(__file__).with_name('package-macos.sh'), app, args.version, unsigned)
        signed = temp / 'signed.pkg'
        run('productsign', '--sign', args.installer_identity, '--timestamp', unsigned, signed)
        run('pkgutil', '--check-signature', signed)
        run('xcrun', 'notarytool', 'submit', signed, '--keychain-profile',
            args.notary_profile, '--wait')
        run('xcrun', 'stapler', 'staple', signed)
        run('xcrun', 'stapler', 'validate', signed)
        run('spctl', '--assess', '--type', 'install', '--verbose=2', signed)
        # Only expose the final output after signing and all notarization checks pass.
        shutil.copy2(signed, output)
        print(f'Validated notarized installer: {output}')


if __name__ == '__main__':
    main()
