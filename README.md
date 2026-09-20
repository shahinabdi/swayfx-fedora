# Fedora SwayFX

Fedora-native installation and configuration for a focused SwayFX desktop: solid dark surfaces, restrained FX, compact status information, and keyboard-first workflows.

> **KDE coexistence:** This project does not replace KDE. It installs SwayFX as an additional desktop session. Existing KDE Plasma and SDDM configuration are left untouched.

## Features

- Full-screen, keyboard-driven terminal UI (dark theme, blue accents) that works over SSH and in a plain terminal
- Fedora package detection through `rpm` and `dnf`, with optional Flatpak support
- Full Setup, Configure Desktop, Applications, Custom Installation, Doctor, and Uninstall / Restore modes
- Custom Installation checkbox screen with per-category selection, select all/none/defaults, and a live search filter
- Live install progress with a percentage bar and per-package status icons; raw `dnf` output is hidden unless `--verbose` is passed
- Idempotent package planning that skips installed packages and reports unavailable packages
- Timestamped backups under `~/.local/state/fedora-swayfx/backups/`
- Manifest-based uninstall that removes only project-managed files
- SwayFX, Waybar, Wofi, Mako, Swaylock, Swayidle, Alacritty, screenshots, lock, and power menu defaults
- `doctor` checks for packages, Wayland, PipeWire, NetworkManager, session files, scripts, and wallpapers
- No hardcoded username or home directory; no Arch package-manager commands

## Install

Clone the repository, then run as your normal user:

```bash
python3 install.py
```

Running `fedora-swayfx` (or `python3 install.py`) with no arguments in an interactive terminal launches the full-screen setup UI. The installer uses `sudo` only for package operations. Run with `--dry-run` to inspect package and configuration decisions without changes, and `--verbose` to see raw `dnf`/`flatpak` output for debugging. Installed configuration is selected through prompts when an existing directory is found; the default replacement path creates a backup first.

For non-interactive / scripted workflows, pass a command directly to skip the UI:

```bash
fedora-swayfx full
fedora-swayfx configure
fedora-swayfx apps
fedora-swayfx doctor
fedora-swayfx uninstall
```

Install the package locally with `pip install .` to make the `fedora-swayfx` command available, or use `python3 install.py` directly.

## Custom applications

The Custom Installation screen presents the package catalog grouped as Core, Terminal, Utilities, and Applications. Use Space to toggle a package, Space on a category header to toggle the whole category, `A`/`N`/`D` for select all / none / defaults, and `/` to search/filter by name. Alacritty is the default terminal; Foot and Kitty remain available as alternatives. Package availability is checked before installation because Fedora repositories and Flatpak remotes vary.

## Configuration

The visual controls live near the top of `configs/swayfx/config` in one variable block: palette (`$bg`, `$accent`, `$secondary`, `$text`, `$muted_text`), layout (`$gap_inner`, `$gap_outer`, `$border_width`), and FX (`$corner_radius`, `$shadow_blur_radius`, `$blur_radius`, `$blur_passes`, `$dim_inactive`, `$animation_duration_ms`). Waybar, Wofi, Mako, Swaylock, and Alacritty ship with matching colors of their own since they can't read Sway variables. Put personal wallpapers in `~/.config/swayfx/wallpapers/`; `scripts/wallpaper.sh` picks the first image found there and falls back to a solid background color, and the installer never downloads a random image.

Default bindings include `$mod+Return` terminal, `$mod+d` launcher, `$mod+q` close, `$mod+Shift+c` reload, `$mod+Shift+e` exit, `$mod+1..9` workspaces, `$mod+Shift+1..9` move, `$mod+f` fullscreen, `$mod+space` floating, `Print` screenshot, `Shift+Print` area screenshot, and `$mod+l` lock.

## Troubleshooting

Run `fedora-swayfx doctor` first. Confirm `swayfx.desktop` appears in `/usr/share/wayland-sessions/`, then choose SwayFX from SDDM without changing KDE’s default session. If a package is unavailable, enable the Fedora repository or COPR appropriate for your Fedora release and rerun; the installer will not substitute Arch commands or silently install a different compositor.

## Development

```bash
python3 -m unittest discover -s tests
python3 -m compileall installer install.py
```

The code uses only the Python standard library. System interactions are kept behind injectable runners so package planning and detection can be tested without a Fedora host.
