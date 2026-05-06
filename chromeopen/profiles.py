from __future__ import annotations

import re
from pathlib import Path

from chromeopen.settings import load_settings, save_settings


CHROME_CONFIG_DIR = Path.home() / ".config" / "google-chrome"
PROFILE_RE = re.compile(r"^Profile \d+$")


def _all_profiles() -> list[str]:
    """Return every Chrome profile directory name, regardless of ignore list."""
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


def list_profiles(include_ignored: bool = False) -> list[str]:
    """Return active (non-ignored) profiles, or all profiles when include_ignored=True."""
    all_profiles = _all_profiles()
    if include_ignored:
        return all_profiles
    ignored = set(load_settings().get("ignored_profiles", []))
    return [p for p in all_profiles if p not in ignored]


def ignored_profiles() -> list[str]:
    """Return the list of profiles currently ignored by chromeopen."""
    all_p = set(_all_profiles())
    return sorted(p for p in load_settings().get("ignored_profiles", []) if p in all_p)


def remove_profile(name: str) -> None:
    """Add *name* to the ignored-profiles list so chromeopen skips it."""
    settings = load_settings()
    ignored: list[str] = settings.get("ignored_profiles", [])
    if name not in ignored:
        ignored.append(name)
        settings["ignored_profiles"] = ignored
        save_settings(settings)


def remove_all_profiles() -> list[str]:
    """Ignore every currently active profile. Returns the list that was ignored."""
    active = list_profiles()
    settings = load_settings()
    ignored: list[str] = settings.get("ignored_profiles", [])
    added = [p for p in active if p not in ignored]
    ignored.extend(added)
    settings["ignored_profiles"] = ignored
    save_settings(settings)
    return added


def restore_profile(name: str) -> None:
    """Remove *name* from the ignored-profiles list."""
    settings = load_settings()
    ignored: list[str] = settings.get("ignored_profiles", [])
    if name in ignored:
        ignored.remove(name)
        settings["ignored_profiles"] = ignored
        save_settings(settings)


def restore_all_profiles() -> None:
    """Clear the ignored-profiles list so all profiles are active again."""
    settings = load_settings()
    settings["ignored_profiles"] = []
    save_settings(settings)
