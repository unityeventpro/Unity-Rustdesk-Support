#!/usr/bin/env python3
"""Patch the pinned client while retaining RustDesk's install/service identity."""
from pathlib import Path
import sys

API_SERVER = 'https://support.unityavs.com'
DESKTOP_LABEL = 'Unity AVS Support'


def replace_once(text, old, new, label):
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f'Expected one pinned {label} patch target; found {text.count(old)}')
    return text.replace(old, new, 1)


def patch(root):
    root = Path(root)
    config = root / 'libs/hbb_common/src/config.rs'
    windows = root / 'src/platform/windows.rs'
    config_text = replace_once(
        config.read_text(),
        '    pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default();',
        '''    pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = {
        let mut settings = HashMap::new();
        #[cfg(windows)]
        {
            settings.insert("custom-rendezvous-server".to_owned(), "codehalter.does-it.net".to_owned());
            settings.insert("relay-server".to_owned(), "codehalter.does-it.net:21117".to_owned());
            settings.insert("api-server".to_owned(), "https://support.unityavs.com".to_owned());
            settings.insert("key".to_owned(), "Ywyx6CcyXMZBa1XwZDshiiXXtkwReMJ4ejXaE6u4CkM=".to_owned());
            if option_env!("UNITY_PRESET_PASSWORD_CONFIG").is_some() {
                settings.insert("verification-method".to_owned(), "use-permanent-password".to_owned());
                settings.insert("approve-mode".to_owned(), "password".to_owned());
            }
        }
        RwLock::new(settings)
    };''',
        'default server settings',
    )
    config_text = replace_once(
        config_text,
        '    pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = Default::default();',
        '''    pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = {
        #[cfg(windows)]
        let settings = option_env!("UNITY_PRESET_PASSWORD_CONFIG")
            .map(|value| serde_json::from_str::<HashMap<String, String>>(value)
                .expect("Invalid unattended access build configuration"))
            .unwrap_or_default();
        #[cfg(not(windows))]
        let settings = HashMap::new();
        RwLock::new(settings)
    };''',
        'build-time permanent password verifier',
    )
    text = windows.read_text()
    old = r'"copy /Y \"{}\\{}.lnk\" \"%PUBLIC%\\Desktop\\\"",'
    new = r'''"if exist \"%PUBLIC%\\Desktop\\RustDesk.lnk\" del /f /q \"%PUBLIC%\\Desktop\\RustDesk.lnk\"
copy /Y \"{}\\{}.lnk\" \"%PUBLIC%\\Desktop\\Unity AVS Support.lnk\"",'''
    text = replace_once(text, old, new, 'desktop shortcut destination')
    old = r'    if exist \"%PUBLIC%\\Desktop\\{app_name}.lnk\" del /f /q \"%PUBLIC%\\Desktop\\{app_name}.lnk\"'
    new = old + '\n' + r'    if exist \"%PUBLIC%\\Desktop\\Unity AVS Support.lnk\" del /f /q \"%PUBLIC%\\Desktop\\Unity AVS Support.lnk\"'
    text = replace_once(text, old, new, 'uninstall shortcut cleanup')
    # Validate every patch before writing either source file.
    config.write_text(config_text)
    windows.write_text(text)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: apply-windows-defaults.py RUSTDESK_SOURCE')
    patch(sys.argv[1])
