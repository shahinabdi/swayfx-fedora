from __future__ import annotations

import configparser
import os
from pathlib import Path

from .detector import Detector


class Doctor:
    def __init__(self, detector: Detector | None = None) -> None:
        self.detector = detector or Detector()

    def report(self) -> list[tuple[str, str, str]]:
        detection = self.detector.detect()
        rows = [
            ("Fedora", "PASS" if detection.fedora else "FAIL", detection.fedora_version),
            ("Wayland", "PASS" if detection.wayland else "WARN", "session available" if detection.wayland else "not detected"),
            ("KDE coexistence", "PASS", "detected and untouched" if detection.kde else "not installed"),
            ("SDDM", "PASS" if detection.sddm else "WARN", "installed" if detection.sddm else "not installed"),
        ]
        for name in ("swayfx", "waybar", "wofi", "mako", "swaylock", "swayidle", "swaybg"):
            present = detection.packages.get(name, self.detector.package_installed(name))
            rows.append((name, "PASS" if present else "FAIL", "installed" if present else "missing"))
        for command in ("pipewire", "nmcli", "grim", "slurp", "swaymsg"):
            present = self.detector.command_exists(command)
            rows.append((command, "PASS" if present else "WARN", "available" if present else "not found"))
        rows.append(("Session file", "PASS" if self._session_available() else "WARN", "Sway session registered" if self._session_available() else "not found"))
        rows.append(("Wallpaper", "PASS" if self._wallpaper_available() else "WARN", "user wallpaper found" if self._wallpaper_available() else "add one under ~/.config/swayfx/wallpapers"))
        return rows

    def _session_available(self) -> bool:
        return any(path.exists() for path in (Path("/usr/share/wayland-sessions/swayfx.desktop"), Path("/usr/share/wayland-sessions/sway.desktop")))

    def _wallpaper_available(self) -> bool:
        wallpaper_dir = Path.home() / ".config" / "swayfx" / "wallpapers"
        return any(wallpaper_dir.glob(pattern) for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"))

    def format(self) -> str:
        return "\n".join(f"{status:4}  {name:18} {detail}" for name, status, detail in self.report())
