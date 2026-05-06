from __future__ import annotations

import json
import os
import re
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

from chromeopen.profiles import _all_profiles, CHROME_CONFIG_DIR
from chromeopen.settings import CONFIG_DIR

# Regex matches http/https/file/chrome URLs up to a null byte or control char
_URL_RE = re.compile(rb"(?:https?|file|chrome)://[\x20-\x7e]{2,800}(?=[\x00-\x1f]|$)")

SNAPSHOTS_DIR = CONFIG_DIR / "snapshots"


def _latest_tabs_file(profile: str) -> Path | None:
    """Return the most recently modified Tabs_* session file for a profile, or None."""
    sessions_dir = CHROME_CONFIG_DIR / profile / "Sessions"
    if not sessions_dir.exists():
        return None
    candidates = sorted(
        sessions_dir.glob("Tabs_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _read_tabs(tabs_file: Path) -> list[str]:
    """Extract unique tab URLs from a Chrome SNSS Tabs_* binary file."""
    # Copy the file to avoid locking issues while Chrome is running
    with tempfile.NamedTemporaryFile(suffix=".snss", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        shutil.copy2(tabs_file, tmp_path)
        data = Path(tmp_path).read_bytes()
    finally:
        os.unlink(tmp_path)

    seen: dict[str, bool] = {}
    for match in _URL_RE.finditer(data):
        url = match.group(0).decode("utf-8", errors="replace").rstrip()
        # Deduplicate while preserving order; skip internal chrome:// NTP duplicates
        canonical = url.rstrip("/")
        if canonical not in seen:
            seen[canonical] = True
    return list(seen.keys())


def take_snapshot() -> Path:
    """
    Capture the currently open tabs for every Chrome profile that has a
    Sessions/Tabs_* file.  Saves a JSON snapshot and returns its path.
    """
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot: dict[str, list[str]] = {}

    for profile in _all_profiles():
        tabs_file = _latest_tabs_file(profile)
        if tabs_file is None:
            continue
        tabs = _read_tabs(tabs_file)
        if tabs:
            snapshot[profile] = tabs

    out_path = SNAPSHOTS_DIR / f"snapshot_{timestamp}.json"
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return out_path


def list_snapshots() -> list[Path]:
    """Return saved snapshot files sorted newest-first."""
    if not SNAPSHOTS_DIR.exists():
        return []
    return sorted(SNAPSHOTS_DIR.glob("snapshot_*.json"), reverse=True)


def load_snapshot(path: Path) -> dict[str, list[str]]:
    """Load and return a snapshot dict from a JSON file."""
    return json.loads(path.read_text())
