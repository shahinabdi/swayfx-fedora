from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from .models import BackupRecord


class BackupManager:
    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = state_dir or Path.home() / ".local" / "state" / "fedora-swayfx"
        self.backup_dir = self.state_dir / "backups"
        self.manifest = self.state_dir / "manifest.json"

    def backup(self, path: Path) -> BackupRecord | None:
        if not path.exists() and not path.is_symlink():
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = self.backup_dir / stamp / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)
        return BackupRecord(path, destination)

    def record(self, paths: list[Path]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.manifest.write_text(json.dumps([str(path) for path in paths], indent=2) + "\n", encoding="utf-8")

    def owned_paths(self) -> list[Path]:
        if not self.manifest.exists():
            return []
        try:
            return [Path(value) for value in json.loads(self.manifest.read_text(encoding="utf-8"))]
        except (OSError, ValueError):
            return []

    def restore_latest(self, path: Path) -> bool:
        candidates = sorted(self.backup_dir.glob(f"*/{path.name}"), reverse=True)
        if not candidates:
            return False
        source = candidates[0]
        if path.exists() or path.is_symlink():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, path)
        else:
            shutil.copy2(source, path)
        return True
