from __future__ import annotations

import logging
import tomllib
from pathlib import Path

from .backup import BackupManager
from .config_manager import ConfigManager
from .detector import Detector
from .models import ConfigAction, InstallMode, InstallPlan, PackageSpec
from .package_manager import PackageManager, ProgressCallback
from .ui import choose_configs, choose_packages, confirm

LOGGER = logging.getLogger(__name__)


class Installer:
    def __init__(self, repository: Path | None = None, dry_run: bool = False, verbose: bool = False) -> None:
        self.repository = repository or Path(__file__).resolve().parent.parent
        self.dry_run = dry_run
        self.verbose = verbose
        self.detector = Detector()
        self.packages = PackageManager(dry_run=dry_run)
        self.config = ConfigManager(self.repository, backup=BackupManager(), dry_run=dry_run)

    def package_catalog(self) -> list[PackageSpec]:
        result: list[PackageSpec] = []
        for filename in ("core.toml", "optional.toml"):
            data = tomllib.loads((self.repository / "packages" / filename).read_text(encoding="utf-8"))
            result.extend(PackageSpec(**item) for item in data["packages"])
        return result

    def default_packages(self, mode: InstallMode) -> list[PackageSpec]:
        catalog = self.package_catalog()
        if mode == InstallMode.APPS:
            return [item for item in catalog if item.category == "Applications" and item.default]
        if mode == InstallMode.FULL:
            return [item for item in catalog if item.category != "Applications" and item.default]
        return [item for item in catalog if item.default]

    def summary(self) -> str:
        found = self.detector.detect([item.name for item in self.package_catalog()])
        lines = [f"Fedora: {'detected' if found.fedora else 'not detected'} {found.fedora_version} {found.architecture}",
                 f"KDE Plasma: {'detected' if found.kde else 'not detected'}", f"SDDM: {'detected' if found.sddm else 'not detected'}",
                 f"Wayland: {'available' if found.wayland else 'not detected'}", f"GPU: {found.gpu}"]
        lines.extend(f"{name}: {'installed' if state else 'not installed'}" for name, state in found.packages.items())
        return "\n".join(lines)

    def run(self, mode: InstallMode, selected: list[PackageSpec] | None = None, action: ConfigAction | None = None) -> bool:
        print(self.summary())
        if mode == InstallMode.UNINSTALL:
            if not self.dry_run and not confirm("Remove project-managed configuration and optionally packages?", False):
                return False
            self.config.uninstall()
            return True
        packages = selected or (self.default_packages(mode) if mode != InstallMode.CONFIGURE else [])
        if mode == InstallMode.CUSTOM:
            packages = choose_packages(self.package_catalog())
        elif mode == InstallMode.APPS and selected is None:
            packages = choose_packages([item for item in self.package_catalog() if item.category == "Applications"])
        if mode in (InstallMode.FULL, InstallMode.APPS, InstallMode.CUSTOM, InstallMode.REPAIR):
            plan = self.packages.plan(packages)
            if plan.unavailable:
                print("Unavailable packages: " + ", ".join(item.name for item in plan.unavailable))
            if not self.packages.install(plan.to_install, verbose=self.verbose):
                return False
        if mode in (InstallMode.FULL, InstallMode.CONFIGURE, InstallMode.CUSTOM, InstallMode.REPAIR):
            if action is None and any(self.config.home.joinpath(".config", name).exists() for name in ConfigManager.CONFIG_MAP):
                action = choose_configs()
            self.config.install(action or ConfigAction.BACKUP_REPLACE)
        return True

    def install_packages(self, packages: list[PackageSpec], on_progress: ProgressCallback | None = None) -> tuple[InstallPlan, bool]:
        """Plan and install a package selection, reporting per-package progress for UI consumers."""

        plan = self.packages.plan(packages)
        success = self.packages.install(plan.to_install, verbose=self.verbose, on_progress=on_progress)
        return plan, success
