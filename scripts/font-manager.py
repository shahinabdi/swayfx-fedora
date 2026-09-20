#!/usr/bin/env python3
"""Choose one installed font and apply it to the desktop configuration."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


HOME = Path.home()
CONFIG = HOME / ".config"
FONT_PATTERN = re.compile(r"^[^,]+")
TARGETS = {
    "Alacritty": [(CONFIG / "alacritty/alacritty.toml", r'^(normal = \{ family = )"[^"]+"', r'\1"{font}"')],
    "Waybar": [(CONFIG / "waybar/style.css", r'^(\* \{ font-family: )"[^"]+"', r'\1"{font}"')],
    "Wofi": [(CONFIG / "wofi/style.css", r'^(window .* font-family: )"[^"]+"', r'\1"{font}"')],
    "Mako": [(CONFIG / "mako/config", r'^(font=)[^\n]+', r'\1{font} 12')],
    "Swaylock": [(CONFIG / "swaylock/config", r'^(font=)[^\n]+', r'\1{font}')],
    "SwayFX": [(CONFIG / "swayfx/config", r'^(font pango:).+$', r'\1{font} 10')],
}


def installed_fonts() -> list[str]:
    result = subprocess.run(
        ["fc-list", ":", "family"],
        capture_output=True,
        text=True,
        check=False,
    )
    fonts = {
        match.group(0).strip()
        for line in result.stdout.splitlines()
        if (match := FONT_PATTERN.match(line.strip()))
    }
    return sorted(font for font in fonts if font)


def choose(items: list[str], prompt: str) -> str | None:
    result = subprocess.run(
        ["wofi", "--dmenu", "--prompt", prompt, "--insensitive"],
        input="\n".join(items),
        capture_output=True,
        text=True,
        check=False,
    )
    selected = result.stdout.strip()
    return selected if selected in items else None


def replace(path: Path, pattern: str, replacement: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count == 0 or updated == text:
        return False
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(updated)
        temporary = Path(handle.name)
    os.replace(temporary, path)
    return True


def apply_font(font: str, target: str) -> int:
    changes = [
        (path, pattern, replacement.format(font=font))
        for path, pattern, replacement in (
            item for name, items in TARGETS.items() if target == "All" or name == target for item in items
        )
    ]
    return sum(replace(path, pattern, replacement) for path, pattern, replacement in changes)


def reload_desktop() -> None:
    for command in (
        ["swaymsg", "reload"],
        ["pkill", "-SIGUSR2", "waybar"],
        ["makoctl", "reload"],
    ):
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def notify(message: str) -> None:
    if not shutil.which("notify-send"):
        return
    subprocess.run(["notify-send", "Font manager", message], check=False)


def main() -> int:
    fonts = installed_fonts()
    if not fonts:
        notify("No installed fonts were found")
        return 0
    target = choose(["All", *TARGETS], "Configure")
    if target is None:
        return 0
    selected = choose(fonts, "Font")
    if selected is None:
        return 0
    if apply_font(selected, target):
        reload_desktop()
        notify(f"Applied {selected} to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())