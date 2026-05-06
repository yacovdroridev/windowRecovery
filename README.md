# ChromeOpen

ChromeOpen recovers Google Chrome profiles after a reboot or crash on Linux. It launches one Chrome window per profile, optionally restores the last session, lets you exclude profiles from recovery, and can snapshot all currently open tabs across every profile.

## Requirements

- Python 3.9+
- Google Chrome installed (`google-chrome` on PATH)
- Tkinter for the settings UI (optional)

On Ubuntu/Debian, install Tkinter with:

```bash
sudo apt-get install python3-tk
```

## Installation

### pip (recommended)

```bash
pip install .
```

This installs the `chromeopen` command on your PATH.

### Without installing

Run directly from the repository root using the wrapper script:

```bash
./scripts/chromeopen <command>
```

## Usage

```
chromeopen list                       # List active (non-ignored) Chrome profiles
chromeopen list-ignored               # List ignored profiles
chromeopen recover                    # Launch one Chrome window per active profile
chromeopen settings                   # Open the settings GUI

chromeopen remove-profile "Profile 2" # Ignore a specific profile
chromeopen remove-all-profiles        # Ignore all profiles
chromeopen restore-profile "Profile 2"# Re-enable a specific ignored profile
chromeopen restore-all-profiles       # Re-enable all ignored profiles

chromeopen snapshot                   # Capture open tabs for all profiles → JSON
chromeopen snapshot --list            # List saved snapshot files
chromeopen snapshot --show FILE       # Print a saved snapshot

chromeopen enable-autostart           # Enable recovery on login (systemd user service)
chromeopen disable-autostart          # Disable autostart
```

Running `chromeopen` with no arguments opens the settings GUI.

## What it does

- Discovers Chrome profiles under `~/.config/google-chrome/` (`Default`, `Profile 1`, …).
- Launches one Chrome window per **active** (non-ignored) profile with `--new-window`.
- Optionally passes `--restore-last-session` (enabled by default, configurable in settings).

## Profile management

Profiles can be **removed** (ignored) so chromeopen skips them during recovery. They are not deleted from disk — only excluded from chromeopen's operations. Use `restore-profile` or `restore-all-profiles` to re-enable them.

The ignore list is stored in `~/.config/chromeopen/settings.json` under `ignored_profiles`.

## Snapshots

`chromeopen snapshot` reads Chrome's binary session files (`Sessions/Tabs_*`) for every profile and extracts the currently open tab URLs. The result is saved as a timestamped JSON file under `~/.config/chromeopen/snapshots/`.

```
~/.config/chromeopen/snapshots/snapshot_20260506T120000Z.json
```

Example output:

```json
{
  "Default": [
    "https://github.com",
    "https://mail.google.com/mail/u/0/#inbox"
  ],
  "Profile 2": [
    "https://www.youtube.com/watch?v=..."
  ]
}
```

> **Note:** Chrome must be running (or have been running since last login) for the session files to contain tabs. Snapshots reflect the last-known open tabs — not a live query through the Chrome DevTools Protocol.

## Autostart

Autostart registers a **systemd user service** at `~/.config/systemd/user/chromeopen.service` that runs `chromeopen recover` after you log in to a graphical session.

Enable / disable via the settings UI or the command line:

```bash
chromeopen enable-autostart
chromeopen disable-autostart
```

## Settings

Settings are stored in `~/.config/chromeopen/settings.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `restore_last_session` | `true` | Pass `--restore-last-session` to Chrome |
| `autostart` | `false` | Launch recovery on login |
| `ignored_profiles` | `[]` | Profiles chromeopen should skip |

## Development

```bash
# Install in editable mode
pip install -e .

# Run directly
python -m chromeopen list
python -m chromeopen snapshot
```

No external dependencies are required beyond the Python standard library.

## License

MIT
