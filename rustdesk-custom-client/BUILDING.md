# Build and download Unity AV Support installers

Use the **Build Unity AV Support installers** workflow on the Actions tab of
`unityeventpro/Unity-Rustdesk-Support`. Select a branch and a platform (or `all`).
The initial `codex/rustdesk-installers` branch also builds when its build files change.
Manual workflow dispatch becomes available after the workflow reaches the default branch.

## Initial targets

| Artifact | Target | Contents |
|---|---|---|
| `UnityAVSupport-windows-x86_64-unsigned` | Windows x64 | EXE opening the native installer and optional administrator helper |
| `UnityAVSupport-macos-x86_64-unsigned` | Intel Mac | PKG installing into /Applications and optional command helper |
| `UnityAVSupport-macos-aarch64-unsigned` | Apple Silicon Mac | PKG installing into /Applications and optional command helper |
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

Download and extract the artifact for the endpoint's architecture. Double-click
`UnityAVSupport-Windows-Install.exe` on Windows and approve installation into
Program Files. Open the Apple Silicon or Intel `.pkg` on macOS and follow Installer;
it installs `/Applications/RustDesk.app`. Open the `.deb` in the Debian/Ubuntu
software installer, or run `sudo apt install ./UnityAVSupport-Linux-amd64.deb`.

Clients do not need the helper scripts or a preconfigured password. The optional
administrator helpers accept `UNITY_SUPPORT_PASSWORD` only when you explicitly
supply a unique per-device unattended password locally. macOS screen recording
and control permissions still require user approval.

`SHA256SUMS` covers the package and supporting files; `build-info.json` records
the target and pinned source. Publish the corresponding source archive beside
any binary release. Never publish signing keys, passwords, or server private keys.

These initial builds are **unsigned and not notarized**. Windows and macOS may
block or warn about downloaded packages. Test only on authorized devices. Developer
ID signing/notarization and Windows Authenticode signing need your own certificates
and are a separate production-release step. The helper scripts can optionally configure a locally
supplied unattended password; they do not bypass OS consent or permissions.
Existing client network settings may override compiled defaults.

## Verify before distribution

Check the displayed logo, confirm the server/key in client settings, connect to the
Linux relay from outside its LAN, and test an authorized support session on each
target OS. Confirm service startup and unattended access after a reboot. A successful
CI build proves compilation and packaging; it does not establish these runtime checks.

## Sign and notarize a Mac release

Keep Developer ID Application and Developer ID Installer identities in the release
Mac's Keychain. Store notarization credentials locally with `xcrun notarytool
store-credentials`; never add credentials or private keys to the repository.

Expand the unsigned candidate with `pkgutil --expand-full candidate.pkg expanded`,
then sign its payload app using the release helper:

```sh
python3 rustdesk-custom-client/scripts/sign-macos.py \
  expanded/Payload/Applications/RustDesk.app output/UnityAVSupport-macOS-AppleSilicon.pkg \
  --identity "Developer ID Application: Your Name (TEAMID)" \
  --installer-identity "Developer ID Installer: Your Name (TEAMID)" \
  --notary-profile UnityRustDesk
```

Use the Intel filename for an Intel candidate. The helper copies the app, signs
nested code inside-out with hardened runtime and the pinned upstream entitlements,
builds and signs the PKG, submits it to Apple, staples the ticket, and validates
Gatekeeper assessment. It only writes the final output after all checks pass.
Recalculate release checksums after signing; candidate checksums no longer apply.
Publish the final native installers, checksums, license and corresponding source
archive together in a GitHub Release. Never label a candidate notarized merely
because it was submitted or its ad-hoc signature verified.

## Windows dashboard enrollment and shortcut

Windows builds default API Server to `https://support.unityavs.com`. A fresh
client sends device inventory/heartbeats to the dashboard without manually
entering this URL. Existing explicit API configuration remains authoritative.
This registers inventory; it does not grant unattended access or automatically
assign a technician address book. No account credentials are embedded.

The desktop shortcut is `Unity AVS Support`; installation, executable and service
identities remain RustDesk for compatibility. Installing with Desktop Icon
selected replaces the old public RustDesk shortcut. Uninstall removes either
shortcut name. The launcher uses an enlarged blue/red monogram with Unity AV Support beneath
it, while the full original artwork remains available for in-app branding.

Pushes build Windows and corresponding source; manual dispatch can still select
Windows, macOS, Linux, or all platforms.
