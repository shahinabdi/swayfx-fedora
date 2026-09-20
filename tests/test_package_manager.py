from __future__ import annotations

import subprocess
import unittest

from installer.models import PackageSpec
from installer.package_manager import PackageManager


class PackageManagerTests(unittest.TestCase):
    def test_plan_separates_installed_and_unavailable(self) -> None:
        def runner(command, **kwargs):
            if command[:2] == ["rpm", "-q"]:
                return subprocess.CompletedProcess(command, 0 if command[-1] == "waybar" else 1, "", "")
            return subprocess.CompletedProcess(command, 0 if command[-1] == "swayfx" else 1, "", "No match for argument")

        manager = PackageManager(runner=runner)
        plan = manager.plan([
            PackageSpec("waybar", "Waybar", "core"),
            PackageSpec("swayfx", "SwayFX", "core"),
            PackageSpec("missing", "Missing", "optional"),
        ])
        self.assertEqual([item.name for item in plan.installed], ["waybar"])
        self.assertEqual([item.name for item in plan.to_install], ["swayfx"])
        self.assertEqual([item.name for item in plan.unavailable], ["missing"])
