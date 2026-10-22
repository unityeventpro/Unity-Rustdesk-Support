# Build and download Unity AV Support installers

Use the **Build Unity AV Support installers** workflow on the Actions tab of
`unityeventpro/Unity-Rustdesk-Support`. Select a branch and a platform (or `all`).
The initial `codex/rustdesk-installers` branch also builds when its build files change.
Manual workflow dispatch becomes available after the workflow reaches the default branch.

## Initial targets

| Artifact | Target | Contents |
|---|---|---|
| `UnityAVSupport-windows-x86_64-unsigned` | Windows x64 | Self-extracting EXE and PowerShell install helper |
| `UnityAVSupport-macos-x86_64-unsigned` | Intel Mac | DMG and command install helper |
| `UnityAVSupport-macos-aarch64-unsigned` | Apple Silicon Mac | DMG and command install helper |
| `UnityAVSupport-linux-x86_64-unsigned` | Debian/Ubuntu amd64 | DEB and shell install helper |
| `UnityAVSupport-RustDesk-source` | All targets | Corresponding modified RustDesk source, submodules and Unity build kit |

These are native builds on GitHub-hosted runners. They can take considerable time,
especially the first vcpkg build. The workflow has a three-hour limit per platform job.
Private-repository builds consume the account's GitHub Actions allowance.
No release is published automatically. Artifacts are kept for 14 days; save the
packages and corresponding source together before distributing them.

The workflow uses the kit's existing RustDesk 1.5.1 commit
`828d1101afd2e656eb1c1d18511009bdf5336238`, including its pinned submodules.
Build steps and toolchain versions are adapted from that commit's official
`flutter-build.yml`, `bridge.yml`, and `third-party-RustDeskTempTopMostWindow.yml`
in https://github.com/rustdesk/rustdesk. Third-party actions use upstream's commit pins.
Upstream dependency downloads and package managers still require network access.
Bridge generation is shared; the initial Windows target uses only its x64 bridge.
When updating RustDesk, compare all three upstream workflows before changing the pin.

The existing logo and `codehalter.does-it.net` server defaults are applied before
building; launcher icons are regenerated using Flutter. The kit's existing server
public key is retained. Verify that it matches `id_ed25519.pub` on your Linux server.
The server's private key and unattended-access passwords are never build inputs.

## Install a test build

Download and extract the artifact for the endpoint's architecture. Keep the package
beside its matching helper. `SHA256SUMS` covers the package and supporting files;
`build-info.json` records the target and pinned RustDesk source commit.
Keep the corresponding source artifact if you distribute the binary under the AGPL.

- **Windows:** Open PowerShell as Administrator. Set `$env:UNITY_SUPPORT_PASSWORD`
  locally to a unique endpoint password, then run `./install-windows.ps1`.
- **macOS:** In Terminal, set and export `UNITY_SUPPORT_PASSWORD` locally, then run
  `bash ./install-macos.command`. Approve administrator authorization and macOS
  Screen Recording/Accessibility permissions as needed for remote support.
- **Debian/Ubuntu:** In a terminal, set and export `UNITY_SUPPORT_PASSWORD` locally,
  then run `bash ./install-linux.sh`.

These initial builds are **unsigned and not notarized**. Windows and macOS may
block or warn about downloaded packages. Test only on authorized devices. Developer
ID signing/notarization and Windows Authenticode signing need your own certificates
and are a separate production-release step. The helper scripts configure a locally
supplied unattended password; they do not bypass OS consent or permissions.
Existing client network settings may override compiled defaults.

## Verify before distribution

Check the displayed logo, confirm the server/key in client settings, connect to the
Linux relay from outside its LAN, and test an authorized support session on each
target OS. Confirm service startup and unattended access after a reboot. A successful
CI build proves compilation and packaging; it does not establish these runtime checks.
