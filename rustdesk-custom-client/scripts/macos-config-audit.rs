    #[cfg(target_os = "macos")]
    if std::env::args().nth(1).as_deref() == Some("--unity-check-defaults") {
        use hbb_common::sha2::{Digest, Sha256};
        // Factory configuration only: no user files, services, network or UI initialization.
        let settings = config::DEFAULT_SETTINGS.read().unwrap();
        let hard = config::HARD_SETTINGS.read().unwrap();
        let storage = hard.get("password").cloned().unwrap_or_default();
        let salt = hard.get("salt").cloned().unwrap_or_default();
        let mut digest = Sha256::new();
        digest.update(storage.as_bytes());
        digest.update(b"\n");
        digest.update(salt.as_bytes());
        let fingerprint = format!("{:x}", digest.finalize());
        println!("{}", hbb_common::serde_json::json!({
            "id_server": settings.get("custom-rendezvous-server"),
            "relay_server": settings.get("relay-server"),
            "api_server": settings.get("api-server"),
            "public_key": settings.get("key"),
            "verification_method": settings.get("verification-method"),
            "approve_mode": settings.get("approve-mode"),
            "permanent_password_usable": config::preset_permanent_password_storage_is_usable_for_auth(&storage, &salt),
            "preset_verifier_fingerprint": fingerprint
        }));
        return None;
    }
