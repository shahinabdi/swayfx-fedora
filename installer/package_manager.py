from __future__ import annotations

import logging
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

from .models import InstallPlan, PackageSpec

LOGGER = logging.getLogger(__name__)


class PackageManager:
    """Small adapter around Fedora package tools; all commands are argument lists."""

    def __init__(self, dry_run: bool = False, runner=subprocess.run) -> None:
        self.dry_run = dry_run
        self.runner = runner

    def _run(self, command: list[str], *, check: bool = False, read_only: bool = False) -> subprocess.CompletedProcess[str]:
        LOGGER.info("%s%s", "DRY RUN: " if self.dry_run else "", " ".join(command))
        if self.dry_run and not read_only:
            return subprocess.CompletedProcess(command, 0, "", "")
        return self.runner(command, text=True, capture_output=True, check=check)

    def installed(self, package: str, manager: str = "dnf") -> bool:
        if manager == "flatpak":
            result = self._run(["flatpak", "info", package], read_only=True)
        else:
            result = self._run(["rpm", "-q", package], read_only=True)
        return result.returncode == 0

    def available(self, package: str, manager: str = "dnf") -> bool:
        if manager == "flatpak":
            return shutil.which("flatpak") is not None
        result = self._run(["dnf", "--assumeno", "install", package], read_only=True)
        return result.returncode == 0 or "No match for argument" not in (result.stdout + result.stderr)

    def plan(self, packages: Iterable[PackageSpec]) -> InstallPlan:
        requested = tuple(packages)
        installed = tuple(item for item in requested if self.installed(item.name, item.manager))
        unavailable = tuple(
            item for item in requested
            if item not in installed and not self.available(item.name, item.manager)
        )
        return InstallPlan(requested, installed, unavailable)

    def install(self, packages: Iterable[PackageSpec], *, retry: bool = True) -> bool:
        grouped: dict[str, list[str]] = {}
        for item in packages:
            grouped.setdefault(item.manager, []).append(item.name)
        success = True
        for manager, names in grouped.items():
            if not names:
                continue
            command = ["sudo", "dnf", "install", "-y", *names] if manager == "dnf" else ["flatpak", "install", "-y", "flathub", *names]
            result = self._run(command)
            if result.returncode != 0 and retry and not self.dry_run:
                LOGGER.warning("Package installation failed; retrying once")
                result = self._run(command)
            success = success and result.returncode == 0
        return success

    def remove(self, packages: Iterable[PackageSpec]) -> bool:
        names = [item.name for item in packages if item.manager == "dnf"]
        if not names:
            return True
        return self._run(["sudo", "dnf", "remove", "-y", *names]).returncode == 0
