#!/usr/bin/env bash
# Sets the desktop wallpaper from ~/.config/swayfx/wallpapers, falling back to
# a solid color that matches the palette background so it never looks broken.
set -euo pipefail

wallpaper_dir="$HOME/.config/swayfx/wallpapers"
bg_color="#0b111a"

pkill -x swaybg >/dev/null 2>&1 || true

image=$(find "$wallpaper_dir" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) 2>/dev/null | sort | head -n1)

if [[ -n "${image:-}" ]]; then
  exec swaybg -i "$image" -m fill
else
  exec swaybg -c "$bg_color"
fi
