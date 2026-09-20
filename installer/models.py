from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class InstallMode(str, Enum):
    FULL = "full"
    CONFIGURE = "configure"
    APPS = "apps"
    CUSTOM = "custom"
    REPAIR = "repair"
    UNINSTALL = "uninstall"


class ConfigAction(str, Enum):
    BACKUP_REPLACE = "backup-replace"
    SKIP = "skip"
    KEEP = "keep"
    CANCEL = "cancel"


# Default keyboard layout applied to the sway config; user is prompted to
# override with QWERTY (us) or a custom layout/variant during install.
DEFAULT_XKB_LAYOUT = "fr"
DEFAULT_XKB_VARIANT = ""
KEYBOARD_LAYOUTS: dict[str, tuple[str, str]] = {
    "azerty": ("fr", ""),
    "qwerty": ("us", ""),
}


@dataclass(frozen=True)
class PackageSpec:
    name: str
    label: str
    category: str
    manager: str = "dnf"
    optional: bool = False
    default: bool = True


@dataclass(frozen=True)
class Detection:
    fedora: bool
    fedora_version: str
    architecture: str
    kde: bool
    sddm: bool
    wayland: bool
    packages: dict[str, bool] = field(default_factory=dict)
    gpu: str = "unknown"
    config_paths: dict[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class InstallPlan:
    requested: tuple[PackageSpec, ...]
    installed: tuple[PackageSpec, ...]
    unavailable: tuple[PackageSpec, ...]

    @property
    def to_install(self) -> tuple[PackageSpec, ...]:
        return tuple(item for item in self.requested if item not in self.installed and item not in self.unavailable)


@dataclass(frozen=True)
class BackupRecord:
    original: Path
    backup: Path
