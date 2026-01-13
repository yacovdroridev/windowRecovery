# ChromeOpen

ChromeOpen helps recover Google Chrome profiles after a reboot or crash on Linux.

## Quick Start
Run from the repository root:

```bash
./scripts/chromeopen list
./scripts/chromeopen recover
./scripts/chromeopen settings
```

The settings UI uses Tkinter. On Ubuntu/Debian, install it with:

```bash
sudo apt-get install python3-tk
```

## What it does
- Discovers Chrome profiles under `~/.config/google-chrome/` (Default, Profile 1, ...).
- Launches one Chrome window per profile.
- Uses `--restore-last-session` when enabled in settings.

## Autostart
Autostart is optional and can be toggled in the settings UI or with:

```bash
./scripts/chromeopen enable-autostart
./scripts/chromeopen disable-autostart
```

Autostart uses a systemd user service at `~/.config/systemd/user/chromeopen.service`.
