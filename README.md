# ChromeOpen

ChromeOpen recovers Google Chrome profiles after a reboot or crash on Linux. It launches one Chrome window per profile and optionally restores the last session.

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
chromeopen list               # List detected Chrome profiles
chromeopen recover            # Launch one Chrome window per profile
chromeopen settings           # Open the settings GUI
chromeopen enable-autostart   # Enable recovery on login (systemd user service)
chromeopen disable-autostart  # Disable autostart
```

Running `chromeopen` with no arguments opens the settings GUI.

## What it does

- Discovers Chrome profiles under `~/.config/google-chrome/` (`Default`, `Profile 1`, …).
- Launches one Chrome window per profile with `--new-window`.
- Optionally passes `--restore-last-session` (enabled by default, configurable in settings).

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

## Development

```bash
# Install in editable mode
pip install -e .

# Run directly
python -m chromeopen list
```

No external dependencies are required beyond the Python standard library.

## License

MIT
