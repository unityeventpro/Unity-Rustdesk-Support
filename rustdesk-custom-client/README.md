# Unity AV Support RustDesk OSS client

This kit applies Unity AV Support branding and your self-hosted server defaults to the RustDesk OSS desktop client. It pins the source snapshot used while preparing this kit to commit `828d1101afd2e656eb1c1d18511009bdf5336238` (RustDesk 1.5.1).

## What is configured

- Client ID server: `codehalter.does-it.net` (RustDesk default port 21116)
- Public key: the public key for your self-hosted RustDesk server
- Logo: the supplied image is used in the client logo slots and as the source image for desktop launcher icons
- Unattended-access password: install scripts read `UNITY_SUPPORT_PASSWORD` from the local environment; no password is embedded in this repository

The server and public key are compiled into the client. An unattended password is optional and can be supplied locally through `UNITY_SUPPORT_PASSWORD`; it is not stored in this repository. Use a unique password per endpoint and only manage devices you own or are authorized to support.

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

Use the repository's [GitHub Actions build workflow](BUILDING.md) to build downloadable test installers on native Windows, macOS, and Linux runners. It generates Windows x64 EXE, Intel and Apple Silicon macOS PKG, and Debian/Ubuntu amd64 DEB bundles, plus a corresponding source archive. Initial packages are unsigned and require platform testing before distribution.

For local builds, RustDesk's desktop Flutter client requires platform-specific toolchains: Windows/MSVC for Windows, macOS/Xcode for macOS, and the Linux build dependencies for Linux. This kit does not assume the current computer has those toolchains installed.

From the customized source tree, follow the official platform build guide and run `python3 build.py --flutter` on that platform:

- [Linux build guide](https://rustdesk.com/docs/en/dev/build/linux/)
- [Windows build guide](https://rustdesk.com/docs/en/dev/build/windows/)
- [macOS build guide](https://rustdesk.com/docs/en/dev/build/osx/)
- [General build guide](https://rustdesk.com/docs/en/dev/build/)

## Client installation

Clients should download individual native installers from a published GitHub Release.
Actions artifacts are temporary build outputs and require additional download steps.

| Download | Install behavior |
|---|---|
| `UnityAVSupport-Windows-Install.exe` | Opens RustDesk's native installation screen; default destination is Program Files/RustDesk |
| `UnityAVSupport-macOS-AppleSilicon.pkg` | macOS Installer places RustDesk.app in /Applications on Apple Silicon Macs |
| `UnityAVSupport-macOS-Intel.pkg` | macOS Installer places RustDesk.app in /Applications on Intel Macs |
| `UnityAVSupport-Linux-amd64.deb` | Debian/Ubuntu amd64 package manager installs the app, launcher, and package files |

A download link downloads a file; the client opens it and approves the normal OS
installation prompts. Browser downloads do not install software without consent.
After installation, open RustDesk and share the displayed ID and one-time password
with the authorized support technician. Mac users must approve screen recording
and control permissions. No password entry in a shell is required for normal use.

The optional administrator helpers are for managed installs. They configure an
unattended password only when `UNITY_SUPPORT_PASSWORD` is explicitly supplied
locally. Do not put passwords in source control or shared installers.

Mac client releases require Developer ID Application and Developer ID Installer
signing plus Apple notarization. Windows builds without Authenticode signing may
show SmartScreen warnings. Keep unsigned candidates clearly identified until the
release signing checks are complete.

## Maintenance

This is a source customization, so rebuild it when updating RustDesk. Review upstream changes to `libs/hbb_common/src/config.rs` and the Flutter asset paths before applying the branding to a newer release. Preserve RustDesk's AGPL notices and provide the corresponding modified source to recipients as required by the license.
