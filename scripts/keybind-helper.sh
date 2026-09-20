#!/usr/bin/env bash
set -euo pipefail

cat <<'KEYBINDS' | wofi --dmenu --prompt "Keybinds" --insensitive
Super+Enter    Open terminal
Super+D        Open application launcher
Super+W        Wallpaper manager
Super+Shift+F  Font and size manager
Super+Shift+T  GTK and Dolphin theme manager
Super+Shift+F1 Keybind helper
Super+Q        Close focused window
Super+F        Toggle fullscreen
Super+Space    Toggle floating window
Super+Ctrl+L   Lock screen
Super+Shift+E  Power menu
Super+Shift+C  Reload Sway configuration
Print          Full screenshot
Shift+Print    Area screenshot
Super+1..9     Switch workspace
Super+Shift+1..9  Move window to workspace
KEYBINDS