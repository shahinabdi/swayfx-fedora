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
Super+E        Toggle horizontal/vertical split
Super+S        Stacking layout
Super+T        Tabbed layout
Super+Shift+S  Horizontal split
Super+Shift+V  Vertical split
Super+R        Resize mode (H/J/K/L or arrows, Enter/Esc exits)
Super+Shift+M  Move mode (H/J/K/L or arrows, Enter/Esc exits)
Super+Shift+Return  Move window to scratchpad
Super+Shift+Space   Show scratchpad
Super+Ctrl+Space    Toggle focus mode
Super+Shift+Tab    Focus parent container
Super+Tab      Focus child container
Super+Ctrl+L   Lock screen
Super+Ctrl+A   Choose AZERTY/QWERTY layout
Super+Ctrl+U   Choose AZERTY/QWERTY layout
Super+Shift+E  Power menu
Super+Shift+C  Reload Sway configuration
Print          Full screenshot
Shift+Print    Area screenshot
Super+1..9     Switch workspace
Super+Shift+1..9  Move window to workspace
KEYBINDS