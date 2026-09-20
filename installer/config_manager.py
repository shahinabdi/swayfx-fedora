from __future__ import annotations

import shutil
from pathlib import Path

from .backup import BackupManager
from .models import ConfigAction


class ConfigManager:
    CONFIG_MAP = {
        "swayfx": "swayfx",
        "waybar": "waybar",
        "wofi": "wofi",
        "mako": "mako",
        "swaylock": "swaylock",
        "alacritty": "alacritty",
    }

    def __init__(self, repository: Path, home: Path | None = None, backup: BackupManager | None = None, dry_run: bool = False) -> None:
        self.repository = repository
        self.home = home or Path.home()
        self.backup = backup or BackupManager()
        self.dry_run = dry_run

    def install(self, action_for_existing: ConfigAction) -> list[Path]:
        changed: list[Path] = []
        for source_name, target_name in self.CONFIG_MAP.items():
            source = self.repository / "configs" / source_name
            target = self.home / ".config" / target_name
            if not source.exists():
                continue
            if target.exists() and action_for_existing in (ConfigAction.KEEP, ConfigAction.SKIP):
                continue
            if target.exists() and action_for_existing == ConfigAction.CANCEL:
                raise RuntimeError("Configuration installation cancelled")
            if not self.dry_run:
                if target.exists():
                    self.backup.backup(target)
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)
            changed.append(target)
        scripts_source = self.repository / "scripts"
        scripts_target = self.home / ".config" / "swayfx" / "scripts"
        if scripts_source.exists() and not (scripts_target.exists() and action_for_existing in (ConfigAction.KEEP, ConfigAction.SKIP)):
            if scripts_target.exists() and action_for_existing == ConfigAction.CANCEL:
                raise RuntimeError("Configuration installation cancelled")
            if not self.dry_run:
                if scripts_target.exists():
                    self.backup.backup(scripts_target)
                    shutil.rmtree(scripts_target)
                scripts_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(scripts_source, scripts_target)
                for script in scripts_target.iterdir():
                    script.chmod(script.stat().st_mode | 0o111)
            changed.append(scripts_target)
        if changed and not self.dry_run:
            self.backup.record(changed)
        return changed

    def uninstall(self) -> list[Path]:
        removed: list[Path] = []
        for path in self.backup.owned_paths():
            if path.exists() or path.is_symlink():
                if not self.dry_run:
                    if path.is_dir() and not path.is_symlink():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                removed.append(path)
                if not self.dry_run:
                    self.backup.restore_latest(path)
        return removed
