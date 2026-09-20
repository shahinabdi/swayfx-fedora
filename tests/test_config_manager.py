from __future__ import annotations

from pathlib import Path
import unittest

from installer.config_manager import ConfigManager
from installer.models import ConfigAction


class ConfigManagerTests(unittest.TestCase):
    def test_config_install_is_idempotent_and_tracks_owned_paths(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            repository = tmp_path / "repo"
            (repository / "configs" / "mako").mkdir(parents=True)
            (repository / "configs" / "mako" / "config").write_text("background-color=#000000\n", encoding="utf-8")
            (repository / "scripts").mkdir()
            (repository / "scripts" / "lock.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            home = tmp_path / "home"
            manager = ConfigManager(repository, home=home)
            changed = manager.install(ConfigAction.BACKUP_REPLACE)
            self.assertTrue((home / ".config" / "mako" / "config").exists())
            self.assertTrue((home / ".config" / "swayfx" / "scripts" / "lock.sh").exists())
            self.assertTrue(changed)
            self.assertEqual(manager.install(ConfigAction.KEEP), [])

    def test_bundled_wallpapers_are_merged_without_overwriting_user_files(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            repository = tmp_path / "repo"
            (repository / "assets" / "wallpapers").mkdir(parents=True)
            (repository / "assets" / "wallpapers" / "bundled.jpg").write_bytes(b"bundled")
            home = tmp_path / "home"
            manager = ConfigManager(repository, home=home)

            manager.install(ConfigAction.BACKUP_REPLACE)
            wallpaper_dir = home / ".config" / "swayfx" / "wallpapers"
            self.assertEqual((wallpaper_dir / "bundled.jpg").read_bytes(), b"bundled")

            (wallpaper_dir / "bundled.jpg").write_bytes(b"user")
            manager.install(ConfigAction.BACKUP_REPLACE)
            self.assertEqual((wallpaper_dir / "bundled.jpg").read_bytes(), b"user")
