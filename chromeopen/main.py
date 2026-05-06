from __future__ import annotations

import argparse
import subprocess
from shutil import which

from chromeopen.autostart import disable_autostart, enable_autostart
from chromeopen.profiles import (
    list_profiles,
    ignored_profiles,
    remove_profile,
    remove_all_profiles,
    restore_profile,
    restore_all_profiles,
)
from chromeopen.settings import load_settings
from chromeopen.snapshot import take_snapshot, list_snapshots, load_snapshot
from chromeopen.ui import open_settings_ui


def _chrome_command() -> str | None:
    return which("google-chrome")


def recover_profiles(settings: dict | None = None) -> int:
    settings = settings or load_settings()
    chrome = _chrome_command()
    if not chrome:
        print("google-chrome not found in PATH.")
        return 1

    profiles = list_profiles()
    if not profiles:
        print("No active Chrome profiles found in ~/.config/google-chrome.")
        return 1

    restore_flag = settings.get("restore_last_session", True)
    for profile in profiles:
        cmd = [
            chrome,
            f"--profile-directory={profile}",
            "--new-window",
        ]
        if restore_flag:
            cmd.append("--restore-last-session")
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="chromeopen",
        description="Recover Chrome profiles after restart.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List active Chrome profiles.")
    subparsers.add_parser("list-ignored", help="List ignored Chrome profiles.")
    subparsers.add_parser("recover", help="Launch all active Chrome profiles.")
    subparsers.add_parser("settings", help="Open settings UI.")
    subparsers.add_parser("enable-autostart", help="Enable autostart recovery.")
    subparsers.add_parser("disable-autostart", help="Disable autostart recovery.")

    # remove / restore
    p_remove = subparsers.add_parser(
        "remove-profile", help="Ignore a profile (chromeopen will skip it)."
    )
    p_remove.add_argument("profile", help='Profile name, e.g. "Default" or "Profile 1".')

    subparsers.add_parser(
        "remove-all-profiles",
        help="Ignore all profiles (chromeopen will skip them all).",
    )

    p_restore = subparsers.add_parser(
        "restore-profile", help="Re-enable a previously ignored profile."
    )
    p_restore.add_argument("profile", help='Profile name, e.g. "Default" or "Profile 1".')

    subparsers.add_parser(
        "restore-all-profiles",
        help="Re-enable all ignored profiles.",
    )

    # snapshot
    p_snap = subparsers.add_parser(
        "snapshot", help="Capture open tabs for all Chrome profiles."
    )
    p_snap.add_argument(
        "--list",
        action="store_true",
        help="List saved snapshots instead of taking a new one.",
    )
    p_snap.add_argument(
        "--show",
        metavar="FILE",
        help="Print the contents of a saved snapshot.",
    )

    args = parser.parse_args()

    if args.command == "list":
        profiles = list_profiles()
        for p in profiles:
            print(p)
        return 0 if profiles else 1

    if args.command == "list-ignored":
        profiles = ignored_profiles()
        if not profiles:
            print("No ignored profiles.")
        for p in profiles:
            print(p)
        return 0

    if args.command == "recover":
        return recover_profiles()

    if args.command == "settings" or args.command is None:
        open_settings_ui()
        return 0

    if args.command == "enable-autostart":
        path = enable_autostart()
        print(f"Autostart enabled: {path}")
        return 0

    if args.command == "disable-autostart":
        disable_autostart()
        print("Autostart disabled.")
        return 0

    if args.command == "remove-profile":
        remove_profile(args.profile)
        print(f"Profile '{args.profile}' ignored.")
        return 0

    if args.command == "remove-all-profiles":
        removed = remove_all_profiles()
        if removed:
            for p in removed:
                print(f"Ignored: {p}")
        else:
            print("No active profiles to ignore.")
        return 0

    if args.command == "restore-profile":
        restore_profile(args.profile)
        print(f"Profile '{args.profile}' restored.")
        return 0

    if args.command == "restore-all-profiles":
        restore_all_profiles()
        print("All profiles restored.")
        return 0

    if args.command == "snapshot":
        if args.list:
            snaps = list_snapshots()
            if not snaps:
                print("No snapshots saved.")
            for s in snaps:
                print(s)
            return 0
        if args.show:
            from pathlib import Path
            data = load_snapshot(Path(args.show))
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0
        path = take_snapshot()
        data = load_snapshot(path)
        total = sum(len(v) for v in data.values())
        print(f"Snapshot saved: {path}")
        print(f"  {len(data)} profile(s), {total} tab(s)")
        for profile, tabs in data.items():
            print(f"\n  [{profile}]")
            for tab in tabs:
                print(f"    {tab}")
        return 0

    parser.print_help()
    return 1
