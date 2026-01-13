from __future__ import annotations

import re
from pathlib import Path


CHROME_CONFIG_DIR = Path.home() / ".config" / "google-chrome"
PROFILE_RE = re.compile(r"^Profile \d+$")


def list_profiles() -> list[str]:
    if not CHROME_CONFIG_DIR.exists():
        return []
    profiles = []
    for entry in CHROME_CONFIG_DIR.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name == "Default" or PROFILE_RE.match(name):
            profiles.append(name)
    return sorted(profiles)
