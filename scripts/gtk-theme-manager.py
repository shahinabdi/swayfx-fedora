#!/usr/bin/env python3
"""Choose and persist the default GTK theme for GTK 3 and GTK 4 apps."""

from __future__ import annotations

import configparser
import shutil
import subprocess
from pathlib import Path


HOME = Path.home()
THEME_ROOTS = (
    HOME / ".themes",
    Path("/usr/share/themes"),
    Path("/usr/local/share/themes"),
)
COLOR_SCHEME_ROOTS = (HOME / ".local/share/color-schemes", Path("/usr/share/color-schemes"))


def installed_themes() -> list[str]:
    themes: set[str] = set()
    for root in THEME_ROOTS:
        if not root.is_dir():
            continue
        for theme in root.iterdir():
            if theme.is_dir() and any((theme / version).is_dir() for version in ("gtk-3.0", "gtk-4.0")):
                themes.add(theme.name)
    return sorted(themes, key=str.casefold)


def choose(themes: list[str]) -> str | None:
    result = subprocess.run(
        ["wofi", "--dmenu", "--prompt", "GTK theme", "--insensitive"],
        input="\n".join(themes),
        capture_output=True,
        text=True,
        check=False,
    )
    selected = result.stdout.strip()
    return selected if selected in themes else None


def installed_color_schemes() -> list[str]:
    schemes: set[str] = set()
    for root in COLOR_SCHEME_ROOTS:
        if root.is_dir():
            schemes.update(path.stem for path in root.glob("*.colors"))
    return sorted(schemes, key=str.casefold)


def write_settings(version: str, theme: str) -> None:
    directory = HOME / ".config" / f"gtk-{version}.0"
    path = directory / "settings.ini"
    directory.mkdir(parents=True, exist_ok=True)
    settings = configparser.ConfigParser()
    settings.optionxform = str
    if path.exists():
        settings.read(path, encoding="utf-8")
    if not settings.has_section("Settings"):
        settings.add_section("Settings")
    settings["Settings"]["gtk-theme-name"] = theme
    with path.open("w", encoding="utf-8") as handle:
        settings.write(handle)


def apply_theme(theme: str) -> None:
    for version in ("3", "4"):
        write_settings(version, theme)
    if shutil.which("gsettings"):
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


def apply_dolphin_scheme(scheme: str) -> None:
    path = HOME / ".config" / "kdeglobals"
    settings = configparser.ConfigParser()
    settings.optionxform = str
    if path.exists():
        settings.read(path, encoding="utf-8")
    if not settings.has_section("General"):
        settings.add_section("General")
    settings["General"]["ColorScheme"] = scheme
    with path.open("w", encoding="utf-8") as handle:
        settings.write(handle)


def notify(message: str) -> None:
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "GTK theme manager", message], check=False)


def main() -> int:
    themes = installed_themes()
    color_schemes = installed_color_schemes()
    if not themes and not color_schemes:
        notify("No GTK themes were found")
        return 0
    options = [f"GTK: {theme}" for theme in themes]
    options.extend(f"Dolphin: {scheme}" for scheme in color_schemes)
    selected = choose(options)
    if selected is None:
        return 0
    if selected.startswith("GTK: "):
        theme = selected.removeprefix("GTK: ")
        apply_theme(theme)
        notify(f"GTK default theme: {theme}")
    else:
        scheme = selected.removeprefix("Dolphin: ")
        apply_dolphin_scheme(scheme)
        notify(f"Dolphin color scheme: {scheme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())