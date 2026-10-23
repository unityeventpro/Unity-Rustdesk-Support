#!/usr/bin/env python3
"""Validate the private build input without logging its contents."""
import base64
import json
import os


def load_preset():
    raw = os.environ.get('UNITY_PRESET_PASSWORD_CONFIG', '')
    if not raw:
        raise SystemExit('Missing UNITY_PRESET_PASSWORD_CONFIG repository secret')
    try:
        config = json.loads(raw)
        assert set(config) == {'password', 'salt'}
        assert isinstance(config['salt'], str) and len(config['salt']) >= 32
        assert isinstance(config['password'], str) and config['password'].startswith('00')
        assert len(base64.b64decode(config['password'][2:], validate=True)) == 32
    except (ValueError, TypeError, AssertionError, KeyError):
        raise SystemExit('Invalid permanent password verifier build secret') from None
    return config


if __name__ == '__main__':
    load_preset()
    print('Validated permanent-password verifier; no secret values logged.')
