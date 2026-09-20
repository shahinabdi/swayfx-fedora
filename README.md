# Fedora SwayFX

Fedora-native installation and configuration for a focused SwayFX desktop: solid dark surfaces, restrained FX, compact status information, and keyboard-first workflows.

> **KDE coexistence:** This project does not replace KDE. It installs SwayFX as an additional desktop session. Existing KDE Plasma and SDDM configuration are left untouched.

## Features

- Fedora package detection through `rpm` and `dnf`, with optional Flatpak support
- Interactive Full Setup, Configure Only, Applications Only, Custom Installation, Repair / Reinstall, and Uninstall / Restore modes
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

The installer uses `sudo` only for package operations. Run `python3 install.py --dry-run` to inspect package and configuration decisions without changes. Installed configuration is selected through prompts when an existing directory is found; the default replacement path creates a backup first.

For command-line workflows:

```bash
fedora-swayfx install
fedora-swayfx configure
fedora-swayfx apps
fedora-swayfx doctor
fedora-swayfx uninstall
```

Install the package locally with `pip install .` to make the `fedora-swayfx` command available, or use `python3 install.py` directly.

## Custom applications

Custom Installation presents the package catalog grouped as Core SwayFX, Desktop utilities, Terminal, and Applications. Use `all`, `none`, `default`, or comma-separated item numbers. Alacritty is the default terminal; Foot and Kitty remain available as alternatives. Package availability is checked before installation because Fedora repositories and Flatpak remotes vary.

## Configuration

The visual controls live near the top of `configs/swayfx/config`: `corner_radius`, `shadow`, `blur`, `blur_radius`, `gaps`, `border_width`, and the focused/unfocused colors. Put personal wallpapers in `~/.config/swayfx/wallpapers/`; the installer never downloads a random image.

Default bindings include `$mod+Return` terminal, `$mod+d` launcher, `$mod+q` close, `$mod+Shift+c` reload, `$mod+Shift+e` exit, `$mod+1..9` workspaces, `$mod+Shift+1..9` move, `$mod+f` fullscreen, `$mod+space` floating, `Print` screenshot, `Shift+Print` area screenshot, and `$mod+l` lock.

## Troubleshooting

Run `fedora-swayfx doctor` first. Confirm `swayfx.desktop` appears in `/usr/share/wayland-sessions/`, then choose SwayFX from SDDM without changing KDE’s default session. If a package is unavailable, enable the Fedora repository or COPR appropriate for your Fedora release and rerun; the installer will not substitute Arch commands or silently install a different compositor.

## Development

```bash
python3 -m unittest discover -s tests
python3 -m compileall installer install.py
```

The code uses only the Python standard library. System interactions are kept behind injectable runners so package planning and detection can be tested without a Fedora host.
