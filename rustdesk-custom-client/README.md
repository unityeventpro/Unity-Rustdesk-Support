# Unity AV Support RustDesk OSS client

This kit applies Unity AV Support branding and your self-hosted server defaults to the RustDesk OSS desktop client. It pins the source snapshot used while preparing this kit to commit `828d1101afd2e656eb1c1d18511009bdf5336238` (RustDesk 1.5.1).

## What is configured

- Client ID server: `codehalter.does-it.net` (RustDesk default port 21116)
- Public key: the public key for your self-hosted RustDesk server
- Logo: the supplied image is used in the client logo slots and as the source image for desktop launcher icons
- Unattended-access password: install scripts read `UNITY_SUPPORT_PASSWORD` from the local environment; no password is embedded in this repository

The server and public key are compiled into the client. The unattended password is supplied locally at install time through `UNITY_SUPPORT_PASSWORD`; it is not stored in this repository. Use a unique password per endpoint and only manage devices you own or are authorized to support.

## Prepare the source

Clone the official RustDesk repository at the pinned commit, including submodules, then apply the source branding:

```sh
git clone --recurse-submodules https://github.com/rustdesk/rustdesk.git rustdesk-unity
cd rustdesk-unity
git checkout 828d1101afd2e656eb1c1d18511009bdf5336238
```

Run the kit's branding script against that source tree:

```sh
/path/to/rustdesk-custom-client/scripts/apply-branding.sh /path/to/rustdesk-unity
```

The script makes the source edits idempotently, keeps the logo files from being dropped by RustDesk's PNG ignore rule, and replaces the relevant Flutter and launcher artwork. The RustDesk product name remains “RustDesk”; the logo and server defaults are customized. Run `scripts/build-client.sh /path/to/rustdesk-unity` from this kit to apply branding and build the client using the native platform toolchain. It runs `flutter pub get`, regenerates launcher icons, then invokes `python3 build.py --flutter`.

These compiled defaults apply to fresh installs. Existing RustDesk client settings can take precedence over the defaults; remove the old client configuration or update its network settings when converting an already-used installation.

## Build requirements and commands

RustDesk currently builds the desktop Flutter client with platform-specific toolchains. This Codex host is Debian 13 x86_64, has Rust installed, but does not have Flutter installed. It can produce Linux packages after the official Linux dependencies and Flutter SDK are installed. Windows builds require a Windows/MSVC environment, and macOS builds require macOS/Xcode. The build tools are too platform-specific to make a reliable Windows or macOS installer from this Linux host.

From the customized source tree, follow the official platform build guide and run `python3 build.py --flutter` on that platform:

- [Linux build guide](https://rustdesk.com/docs/en/dev/build/linux/)
- [Windows build guide](https://rustdesk.com/docs/en/dev/build/windows/)
- [macOS build guide](https://rustdesk.com/docs/en/dev/build/osx/)
- [General build guide](https://rustdesk.com/docs/en/dev/build/)

After building, rename the generated packages to `UnityAVSupport-RustDesk.deb`, `UnityAVSupport-RustDesk-Setup.exe`, or `UnityAVSupport-RustDesk.dmg`, then place each package beside its matching install script.

## One-click installation

- Windows: put `install-windows.ps1` beside the `.exe`, then run it as administrator.
- macOS: put `install-macos.command` beside the `.dmg`; it prompts for administrator authorization to copy RustDesk into `/Applications`.
- Debian/Ubuntu: put `install-linux.sh` beside the `.deb` and run it from a terminal; it invokes `sudo` to install the package.

Before running an install script, set `UNITY_SUPPORT_PASSWORD` in the local shell or PowerShell session. Do not put it in source control or a shared installer. Use a unique per-device password. macOS installers need Developer ID code signing and notarization for a low-friction Gatekeeper experience. Unsigned Windows installers can receive SmartScreen warnings.

## Maintenance

This is a source customization, so rebuild it when updating RustDesk. Review upstream changes to `libs/hbb_common/src/config.rs` and the Flutter asset paths before applying the branding to a newer release. Preserve RustDesk's AGPL notices and provide the corresponding modified source to recipients as required by the license.
