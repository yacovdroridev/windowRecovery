from __future__ import annotations

import json
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "chromeopen"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
DEFAULT_SETTINGS: dict = {
    "autostart": False,
    "restore_last_session": True,
    "ignored_profiles": [],
}


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        data = json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()
    merged = DEFAULT_SETTINGS.copy()
    if isinstance(data, dict):
        merged.update({k: data.get(k, v) for k, v in DEFAULT_SETTINGS.items()})
    return merged


def save_settings(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = DEFAULT_SETTINGS.copy()
    payload.update(settings)
    SETTINGS_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True))
