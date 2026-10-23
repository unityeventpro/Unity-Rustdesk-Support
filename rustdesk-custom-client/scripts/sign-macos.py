#!/usr/bin/env python3
"""Sign and submit Mac packages, preserving candidates while Apple processes them."""
import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
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


def json_command(*args):
    result = subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def save_state(path, state):
    path.write_text(json.dumps(state, indent=2) + '\n')


def complete(state_path):
    state = json.loads(state_path.read_text())
    result = json_command('xcrun', 'notarytool', 'info', state['submission_id'],
                          '--keychain-profile', state['notary_profile'], '--output-format', 'json')
    state['notary_status'] = result['status']
    state['last_checked'] = datetime.now(timezone.utc).isoformat()
    save_state(state_path, state)
    if result['status'] == 'In Progress':
        print(f"Apple notarization is pending: {state['submission_id']}")
        return 2
    if result['status'] != 'Accepted':
        log = state_path.with_name('notary-log.json')
        run('xcrun', 'notarytool', 'log', state['submission_id'], '--keychain-profile',
            state['notary_profile'], log)
        raise SystemExit(f"Apple returned {result['status']}; inspect {log}")
    signed = Path(state['signed_candidate'])
    run('xcrun', 'stapler', 'staple', signed)
    run('xcrun', 'stapler', 'validate', signed)
    run('pkgutil', '--check-signature', signed)
    run('spctl', '--assess', '--type', 'install', '--verbose=2', signed)
    output = Path(state['final_output'])
    if output.exists():
        raise SystemExit('Final output already exists; preserve it rather than overwrite')
    shutil.copy2(signed, output)
    state['release_ready'] = True
    save_state(state_path, state)
    print(f'Validated notarized installer: {output}')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('app', type=Path, nargs='?')
    parser.add_argument('output', type=Path, nargs='?')
    parser.add_argument('--identity')
    parser.add_argument('--installer-identity')
    parser.add_argument('--notary-profile', default='UnityRustDesk')
    parser.add_argument('--version', default='1.5.1')
    parser.add_argument('--submit-only', action='store_true')
    parser.add_argument('--resume', type=Path, help='Poll and finish a preserved submission state')
    args = parser.parse_args()
    if args.resume:
        return complete(args.resume.resolve())
    if not all([args.app, args.output, args.identity, args.installer_identity]):
        parser.error('App, output and both signing identities are required for a new submission')
    if not (args.app / 'Contents/MacOS/RustDesk').is_file():
        parser.error('Expected a complete RustDesk.app')
    output = args.output.resolve()
    work = output.with_suffix('.signing')
    if output.exists() or work.exists():
        parser.error('Output/staging path already exists; use --resume or a new output path')
    work.mkdir(parents=True)
    app = work / 'RustDesk.app'
    run('ditto', args.app.resolve(), app)
    entitlements = work / 'Release.entitlements'
    entitlements.write_text(ENTITLEMENTS)
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
    unsigned = work / 'unsigned.pkg'
    run('bash', Path(__file__).with_name('package-macos.sh'), app, args.version, unsigned)
    signed = work / output.name
    run('productsign', '--sign', args.installer_identity, '--timestamp', unsigned, signed)
    run('pkgutil', '--check-signature', signed)
    state_path = work / 'submission.json'
    state = {'app': str(app), 'signed_candidate': str(signed), 'final_output': str(output),
             'notary_profile': args.notary_profile, 'release_ready': False,
             'application_identity': args.identity, 'installer_identity': args.installer_identity,
             'notary_status': 'Signed, not yet submitted'}
    save_state(state_path, state)
    submission = json_command('xcrun', 'notarytool', 'submit', signed, '--keychain-profile',
                              args.notary_profile, '--output-format', 'json')
    state['submission_id'] = submission['id']
    state['notary_status'] = 'In Progress'
    state['submitted_at'] = datetime.now(timezone.utc).isoformat()
    save_state(state_path, state)
    print(f"Signed package submitted: {submission['id']}; preserved state: {state_path}")
    if args.submit_only:
        return 0
    return complete(state_path)


if __name__ == '__main__':
    raise SystemExit(main())
