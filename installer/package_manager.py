from __future__ import annotations

import logging
import shutil
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path

from .models import InstallPlan, PackageSpec

LOGGER = logging.getLogger(__name__)

ProgressCallback = Callable[[PackageSpec, str], None]


class PackageManager:
    """Small adapter around Fedora package tools; all commands are argument lists."""

    def __init__(self, dry_run: bool = False, runner=subprocess.run) -> None:
        self.dry_run = dry_run
        self.runner = runner

    def _run(self, command: list[str], *, check: bool = False, read_only: bool = False, stream: bool = False) -> subprocess.CompletedProcess[str]:
        LOGGER.debug("%s%s", "DRY RUN: " if self.dry_run else "", " ".join(command))
        if self.dry_run and not read_only:
            return subprocess.CompletedProcess(command, 0, "", "")
        if stream:
            return self.runner(command, text=True, check=check)
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

    def install(
        self,
        packages: Iterable[PackageSpec],
        *,
        retry: bool = True,
        verbose: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> bool:
        success = True
        for item in packages:
            if on_progress:
                on_progress(item, "start")
            command = ["sudo", "dnf", "install", "-y", item.name] if item.manager == "dnf" else ["flatpak", "install", "-y", "flathub", item.name]
            result = self._run(command, stream=verbose)
            if result.returncode != 0 and retry and not self.dry_run:
                LOGGER.warning("Package installation failed; retrying once")
                result = self._run(command, stream=verbose)
            ok = result.returncode == 0
            if not ok and not verbose:
                LOGGER.debug("%s failed: %s", item.name, (result.stderr or result.stdout or "").strip())
            success = success and ok
            if on_progress:
                on_progress(item, "done" if ok else "failed")
        return success

    def remove(self, packages: Iterable[PackageSpec]) -> bool:
        names = [item.name for item in packages if item.manager == "dnf"]
        if not names:
            return True
        return self._run(["sudo", "dnf", "remove", "-y", *names]).returncode == 0
