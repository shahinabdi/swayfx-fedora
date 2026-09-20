#!/usr/bin/env bash
set -euo pipefail

wallpaper_dir="$HOME/.config/swayfx/wallpapers"

mapfile -t images < <(
  find "$wallpaper_dir" -maxdepth 1 -type f \( \
    -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \
  \) -printf '%f\n' 2>/dev/null | sort
)

if ((${#images[@]} == 0)); then
  notify-send "Wallpaper manager" "Add an image under $wallpaper_dir" 2>/dev/null || true
  exit 0
fi

selected=$(printf '%s\n' "${images[@]}" | wofi --dmenu --prompt "Wallpaper" --insensitive)
[[ -n "$selected" ]] || exit 0

image="$wallpaper_dir/$selected"
[[ -f "$image" ]] || exit 1

pkill -x swaybg >/dev/null 2>&1 || true
exec swaybg -i "$image" -m fill