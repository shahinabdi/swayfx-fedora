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

The visual controls live near the top of `configs/swayfx/config` in one variable block: palette (`$bg`, `$accent`, `$secondary`, `$text`, `$muted_text`), layout (`$gap_inner`, `$gap_outer`, `$border_width`), and FX (`$corner_radius`, `$shadow_blur_radius`, `$blur_radius`, `$blur_passes`, `$dim_inactive`, `$animation_duration_ms`). Waybar, Wofi, Mako, Swaylock, and Alacritty ship with matching colors of their own since they can't read Sway variables. Put bundled wallpapers in `assets/wallpapers/`; Git LFS tracks PNG, JPG, JPEG, and WebP files there, and the installer copies them into `~/.config/swayfx/wallpapers/` without replacing personal files. You can also add personal images through `$mod+w`, which saves the selected wallpaper and restores it at startup. If no selection has been saved, `scripts/wallpaper.sh` uses the first image found there.

The installer supports both AZERTY (French) and QWERTY (US) layouts. It asks for the layout during configuration, and `$mod+Ctrl+a` or `$mod+Ctrl+u` opens a runtime selector that saves the choice and reloads Sway. Default bindings include `$mod+Return` terminal, `$mod+d` launcher, `$mod+q` close, `$mod+Shift+c` reload, `$mod+Shift+e` power menu, `$mod+1..9` workspaces, `$mod+Shift+1..9` move, `$mod+f` fullscreen, `$mod+space` floating, `$mod+e` split toggle, `$mod+s` stacking, `$mod+t` tabbed, `$mod+Shift+s` horizontal split, `$mod+Shift+v` vertical split, `$mod+r` resize mode, `$mod+Shift+m` move mode, `$mod+Shift+Return` scratchpad move, `$mod+Shift+Space` scratchpad show, `$mod+Ctrl+Space` focus mode, `$mod+w` wallpaper manager, `$mod+Shift+f` font manager, `$mod+Shift+t` GTK/Dolphin theme manager, `$mod+Shift+F1` keybind helper, `Print` screenshot, `Shift+Print` area screenshot, and `$mod+Ctrl+l` lock. The regular top-row minus key remains available as an alternate scratchpad binding. The font manager asks which application to update, then the font family and size, so Alacritty and Waybar can differ. The GTK/Dolphin manager writes GTK 3/4 settings and the GNOME theme database; GTK themes control GTK apps, while Dolphin uses the KDE color scheme and may need to be reopened. The lock screen uses the selected wallpaper with fill scaling and recovers to the first available image if the saved file is missing. The wallpaper manager can import one image or all supported images from a folder, then saves the selected wallpaper across Sway and lock-screen restarts. Click the Waybar sound module to open `pavucontrol`.

## Troubleshooting

Run `fedora-swayfx doctor` first. Confirm `swayfx.desktop` appears in `/usr/share/wayland-sessions/`, then choose SwayFX from SDDM without changing KDE’s default session. If a package is unavailable, enable the Fedora repository or COPR appropriate for your Fedora release and rerun; the installer will not substitute Arch commands or silently install a different compositor.

## Development

```bash
python3 -m unittest discover -s tests
python3 -m compileall installer install.py
```

The code uses only the Python standard library. System interactions are kept behind injectable runners so package planning and detection can be tested without a Fedora host.
