from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from installer.detector import Detector


class DetectorTests(unittest.TestCase):
    def test_detector_uses_injected_home_and_runner(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            (tmp_path / ".config" / "waybar").mkdir(parents=True)

            def runner(command, **kwargs):
                return subprocess.CompletedProcess(command, 0 if command[-1] in {"swayfx", "plasma-workspace", "sddm"} else 1, "", "")

            detector = Detector(home=tmp_path, runner=runner)
            result = detector.detect(["swayfx", "waybar"])
            self.assertTrue(result.architecture)
            self.assertEqual(result.packages, {"swayfx": True, "waybar": False})
            self.assertTrue(result.config_paths["waybar"])
            self.assertTrue(result.kde)
            self.assertTrue(result.sddm)
