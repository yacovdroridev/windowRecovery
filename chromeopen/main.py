from __future__ import annotations

import argparse
import subprocess
from shutil import which

from chromeopen.autostart import disable_autostart, enable_autostart
from chromeopen.profiles import list_profiles
from chromeopen.settings import load_settings
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
        print("No Chrome profiles found in ~/.config/google-chrome.")
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

    subparsers.add_parser("list", help="List detected Chrome profiles.")
    subparsers.add_parser("recover", help="Launch all Chrome profiles.")
    subparsers.add_parser("settings", help="Open settings UI.")
    subparsers.add_parser("enable-autostart", help="Enable autostart recovery.")
    subparsers.add_parser("disable-autostart", help="Disable autostart recovery.")

    args = parser.parse_args()

    if args.command == "list":
        profiles = list_profiles()
        for profile in profiles:
            print(profile)
        return 0 if profiles else 1
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

    parser.print_help()
    return 1
