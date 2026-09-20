#!/usr/bin/env bash
# Sets the desktop wallpaper from ~/.config/swayfx/wallpapers, falling back to
# a solid color that matches the palette background so it never looks broken.
set -euo pipefail

wallpaper_dir="$HOME/.config/swayfx/wallpapers"
selected_file="$HOME/.config/swayfx/wallpaper.selected"
bg_color="#0b111a"

pkill -x swaybg >/dev/null 2>&1 || true

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

if [[ -n "${image:-}" ]]; then
  exec swaybg -i "$image" -m fill
else
  exec swaybg -c "$bg_color"
fi
