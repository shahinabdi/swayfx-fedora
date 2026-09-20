from __future__ import annotations

import shutil
from pathlib import Path

from .backup import BackupManager
from .models import DEFAULT_XKB_LAYOUT, DEFAULT_XKB_VARIANT, ConfigAction


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

    def install(
        self,
        action_for_existing: ConfigAction,
        xkb_layout: str = DEFAULT_XKB_LAYOUT,
        xkb_variant: str = DEFAULT_XKB_VARIANT,
    ) -> list[Path]:
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
                if source_name == "swayfx":
                    self._apply_keyboard_layout(target, xkb_layout, xkb_variant)
                    sway_link = self._link_sway_config(target, action_for_existing)
                    if sway_link is not None:
                        changed.append(sway_link)
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

    def _apply_keyboard_layout(self, swayfx_target: Path, xkb_layout: str, xkb_variant: str) -> None:
        config_file = swayfx_target / "config"
        if not config_file.exists():
            return
        text = config_file.read_text(encoding="utf-8")
        text = text.replace("{{XKB_LAYOUT}}", xkb_layout).replace("{{XKB_VARIANT}}", xkb_variant)
        config_file.write_text(text, encoding="utf-8")

    def _link_sway_config(self, swayfx_target: Path, action_for_existing: ConfigAction) -> Path | None:
        # sway only reads ~/.config/sway/config by default, so point it at
        # our installed config or it silently falls back to /etc/sway/config.
        sway_dir = self.home / ".config" / "sway"
        sway_config = sway_dir / "config"
        if sway_config.exists() or sway_config.is_symlink():
            if action_for_existing in (ConfigAction.KEEP, ConfigAction.SKIP):
                return None
            if action_for_existing == ConfigAction.CANCEL:
                raise RuntimeError("Configuration installation cancelled")
            self.backup.backup(sway_config)
            sway_config.unlink()
        sway_dir.mkdir(parents=True, exist_ok=True)
        sway_config.symlink_to(swayfx_target / "config")
        return sway_config

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
