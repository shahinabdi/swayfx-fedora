#!/usr/bin/env bash
set -euo pipefail
# Colors come from ~/.config/swaylock/config to match the rest of the desktop.
wallpaper_dir="$HOME/.config/swayfx/wallpapers"
selected_file="$HOME/.config/swayfx/wallpaper.selected"
image=""

if [[ -f "$selected_file" ]]; then
	selected=$(<"$selected_file")
	if [[ -f "$wallpaper_dir/$selected" ]]; then
		image="$wallpaper_dir/$selected"
	fi
fi

if [[ -z "$image" ]]; then
	image=$(find "$wallpaper_dir" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) 2>/dev/null | sort | head -n1)
fi

if [[ -n "$image" ]]; then
	printf '%s\n' "$(basename "$image")" >"$selected_file"
	swaylock -f -i "$image" -s fill
else
	swaylock -f
fi
