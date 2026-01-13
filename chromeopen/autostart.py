from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SERVICE_NAME = "chromeopen.service"
SYSTEMD_DIR = Path.home() / ".config" / "systemd" / "user"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _service_contents() -> str:
    project_root = _project_root()
    python = sys.executable
    return "\n".join(
        [
            "[Unit]",
            "Description=Chrome profile recovery",
            "",
            "[Service]",
            "Type=oneshot",
            f"WorkingDirectory={project_root}",
            f"Environment=PYTHONPATH={project_root}",
            f"ExecStart={python} -m chromeopen recover",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )


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
    if not shutil_which("systemctl"):
        return
    subprocess.run(["systemctl", *args], check=False)


def shutil_which(command: str) -> bool:
    from shutil import which

    return which(command) is not None
