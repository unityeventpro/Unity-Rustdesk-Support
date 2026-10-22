#!/usr/bin/env python3
"""Collect one native build into a downloadable Unity installer bundle."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def package(platform, arch, source_ref, root=Path('.'), kit=None):
    kit = kit or Path(__file__).resolve().parents[1]
    patterns = {
        'windows': ('SignOutput/rustdesk-*-' + arch + '.exe', 'UnityAVSupport-RustDesk-Setup.exe', 'install-windows.ps1'),
        'macos': ('rustdesk-*-' + arch + '.dmg', 'UnityAVSupport-RustDesk.dmg', 'install-macos.command'),
        'linux': ('rustdesk-*-' + arch + '.deb', 'UnityAVSupport-RustDesk.deb', 'install-linux.sh'),
    }
    pattern, name, helper = patterns[platform]
    candidates = sorted(root.glob(pattern))
    if len(candidates) != 1:
        raise ValueError(f'Expected exactly one {pattern}, found {len(candidates)}')
    if candidates[0].stat().st_size == 0:
        raise ValueError('Build output is empty')
    output = root / 'unity-dist'
    # Avoid accidentally bundling stale binaries from a previous platform build.
    output.mkdir(exist_ok=False)
    shutil.copy2(candidates[0], output / name)
    shutil.copy2(kit / 'scripts' / helper, output / helper)
    (output / helper).chmod(0o755 if platform != 'windows' else 0o644)
    shutil.copy2(root / 'LICENCE', output / 'RUSTDESK-LICENCE.txt')
    shutil.copy2(kit / 'BUILDING.md', output / 'BUILDING.md')
    manifest = {
        'product': 'Unity AV Support RustDesk', 'platform': platform, 'architecture': arch,
        'rustdesk_source_commit': source_ref, 'signed': False,
        'server': 'codehalter.does-it.net',
        'source_artifact': 'UnityAVSupport-RustDesk-source (download from the same workflow run)',
    }
    (output / 'build-info.json').write_text(json.dumps(manifest, indent=2) + '\n')
    hashes = []
    for path in sorted(output.iterdir()):
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
    (output / 'SHA256SUMS').write_text('\n'.join(hashes) + '\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['windows', 'macos', 'linux'], required=True)
    parser.add_argument('--arch', choices=['x86_64', 'aarch64'], required=True)
    parser.add_argument('--source-ref', required=True)
    args = parser.parse_args()
    print(package(args.platform, args.arch, args.source_ref))
