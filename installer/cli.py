from __future__ import annotations

import argparse
import logging
import sys

from .installer import Installer
from .models import ConfigAction, InstallMode
from .doctor import Doctor
from .ui import choose_mode


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="fedora-swayfx", description="Install and configure a Fedora-native SwayFX session")
    result.add_argument("command", nargs="?", choices=[mode.value for mode in InstallMode] + ["doctor"])
    result.add_argument("--dry-run", action="store_true", help="show changes without writing or installing")
    result.add_argument("--yes", action="store_true", help="replace existing configuration without prompting")
    return result


def run(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parser().parse_args(argv)
    installer = Installer(dry_run=args.dry_run)
    try:
        if args.command == "doctor":
            print(Doctor(installer.detector).format())
            return 0
        mode = InstallMode(args.command) if args.command else choose_mode()
        action = ConfigAction.BACKUP_REPLACE if args.yes else None
        return 0 if installer.run(mode, action=action) else 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
