# Unity Rustdesk Support

Private source kit for deploying a Unity AV Support RustDesk OSS relay and preparing branded RustDesk clients.

## Contents

- `rustdesk-server/`: Docker Compose deployment template and server setup notes.
- `rustdesk-custom-client/`: RustDesk OSS source branding and build/install scripts for Windows, macOS, and Linux.

## Security notes

The relay's private key, live database, and `.env` configuration are intentionally excluded. Generate and safeguard the server key on the Linux relay host. The server public key can be distributed to clients.

The install scripts require `UNITY_SUPPORT_PASSWORD` to be set locally before configuring unattended access. Do not commit this value or reuse one shared password across all client machines. Set a unique unattended password per endpoint where supported.

GitHub Actions builds unsigned test installer bundles for Windows x64, Intel and Apple Silicon macOS, and Debian/Ubuntu amd64. See [Build and download installers](rustdesk-custom-client/BUILDING.md) for workflow instructions, artifacts, signing requirements, and runtime checks.
