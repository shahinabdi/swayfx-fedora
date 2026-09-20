from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from .models import Detection


class Detector:
    def __init__(self, home: Path | None = None, runner=subprocess.run) -> None:
        self.home = home or Path.home()
        self.runner = runner

    def command_exists(self, command: str) -> bool:
        return shutil.which(command) is not None

    def package_installed(self, package: str) -> bool:
        result = self.runner(["rpm", "-q", package], capture_output=True, text=True)
        return result.returncode == 0

    def _fedora_release(self) -> tuple[bool, str]:
        release = Path("/etc/fedora-release")
        if not release.exists():
            return False, "unknown"
        text = release.read_text(encoding="utf-8", errors="replace").strip()
        for prefix in ("Fedora Linux release ", "Fedora release "):
            if text.startswith(prefix):
                return True, text.removeprefix(prefix).split(" (")[0]
        return True, text.removeprefix("Fedora Linux release ").split(" (")[0]

    def detect(self, package_names: list[str] | None = None) -> Detection:
        fedora, version = self._fedora_release()
        names = package_names or ["sway", "swayfx", "waybar", "wofi", "mako", "swaylock", "swayidle", "swaybg"]
        packages = {name: self.package_installed(name) for name in names}
        config_names = ["swayfx", "sway", "waybar", "wofi", "mako", "alacritty"]
        config_paths = {name: (self.home / ".config" / name).exists() for name in config_names}
        kde = any(self.package_installed(name) for name in ("plasma-desktop", "plasma-workspace"))
        return Detection(
            fedora=fedora,
            fedora_version=version,
            architecture=platform.machine(),
            kde=kde,
            sddm=self.package_installed("sddm"),
            wayland=bool(os.environ.get("WAYLAND_DISPLAY") or self.command_exists("wayland-info")),
            packages=packages,
            gpu=self._gpu(),
            config_paths=config_paths,
        )

    def _gpu(self) -> str:
        if not self.command_exists("lspci"):
            return "unknown"
        result = self.runner(["lspci"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if " VGA " in line or " 3D controller" in line:
                return line.split(": ", 1)[-1].strip()
        return "unknown"
