#!/usr/bin/env bash
set -euo pipefail
# Colors come from ~/.config/swaylock/config to match the rest of the desktop.
wallpaper_dir="$HOME/.config/swayfx/wallpapers"
selected_file="$HOME/.config/swayfx/wallpaper.selected"

if [[ -f "$selected_file" && -f "$wallpaper_dir/$(<"$selected_file")" ]]; then
	swaylock -f -i "$wallpaper_dir/$(<"$selected_file")" -s fill
else
	swaylock -f
fi
