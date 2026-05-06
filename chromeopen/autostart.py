from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from shutil import which


SERVICE_NAME = "chromeopen.service"
SYSTEMD_DIR = Path.home() / ".config" / "systemd" / "user"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _chromeopen_exec() -> str:
    """Return the best available command to run chromeopen recover."""
    # Prefer an installed entry-point on PATH
    entry = which("chromeopen")
    if entry:
        return entry
    # Fall back to running the package with the current interpreter
    project_root = _project_root()
    return f"env PYTHONPATH={project_root} {sys.executable} -m chromeopen"


def _service_contents() -> str:
    exec_start = _chromeopen_exec()
    # If the exec path contains spaces we need the full env form; split on first space
    # to provide ExecStart correctly for systemd (must be an absolute path or env).
    parts = exec_start.split()
    if parts[0] == "env":
        # systemd doesn't support the env wrapper — embed env var in Environment=
        project_root = _project_root()
        exec_line = f"{sys.executable} -m chromeopen recover"
        env_line = f"Environment=PYTHONPATH={project_root}"
    else:
        exec_line = f"{parts[0]} recover"
        env_line = ""

    lines = [
        "[Unit]",
        "Description=Chrome profile recovery",
        "After=graphical-session.target",
        "",
        "[Service]",
        "Type=oneshot",
    ]
    if env_line:
        lines.append(env_line)
    lines += [
        f"ExecStart={exec_line}",
        "",
        "[Install]",
        "WantedBy=graphical-session.target",
        "",
    ]
    return "\n".join(lines)


def enable_autostart() -> str:
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)
    service_path = SYSTEMD_DIR / SERVICE_NAME
    service_path.write_text(_service_contents())
    _systemctl(["--user", "daemon-reload"])
    _systemctl(["--user", "enable", "--now", SERVICE_NAME])
    return str(service_path)


def disable_autostart() -> None:
    service_path = SYSTEMD_DIR / SERVICE_NAME
    _systemctl(["--user", "disable", "--now", SERVICE_NAME])
    if service_path.exists():
        service_path.unlink()
    _systemctl(["--user", "daemon-reload"])


def _systemctl(args: list[str]) -> None:
    if not which("systemctl"):
        return
    subprocess.run(["systemctl", *args], check=False)
