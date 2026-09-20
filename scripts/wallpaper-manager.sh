#!/usr/bin/env bash
set -euo pipefail

wallpaper_dir="$HOME/.config/swayfx/wallpapers"
selected_file="$HOME/.config/swayfx/wallpaper.selected"
mkdir -p "$wallpaper_dir"

notify() {
  notify-send "Wallpaper manager" "$1" 2>/dev/null || true
}

expand_path() {
  local path="$1"
  path="${path/#\~/$HOME}"
  printf '%s\n' "$path"
}

copy_image() {
  local source="$1"
  [[ -f "$source" ]] || return 1
  case "${source,,}" in
    *.png|*.jpg|*.jpeg|*.webp) cp -- "$source" "$wallpaper_dir/"; return 0 ;;
  esac
  return 1
}

add_file() {
  local source
  source=$(printf '\n' | wofi --dmenu --prompt "Image path" --insensitive)
  [[ -n "$source" ]] || return 0
  source=$(expand_path "$source")
  if copy_image "$source"; then
    notify "Added $(basename "$source")"
  else
    notify "Not a supported image file"
  fi
}

add_folder() {
  local source copied=0
  source=$(printf '\n' | wofi --dmenu --prompt "Folder path" --insensitive)
  [[ -n "$source" ]] || return 0
  source=$(expand_path "$source")
  [[ -d "$source" ]] || { notify "Folder not found"; return 0; }
  while IFS= read -r -d '' image; do
    cp -- "$image" "$wallpaper_dir/"
    copied=$((copied + 1))
  done < <(find "$source" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) -print0)
  notify "Added $copied wallpaper(s)"
}

mapfile -t images < <(
  find "$wallpaper_dir" -maxdepth 1 -type f \( \
    -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \
  \) -printf '%f\n' 2>/dev/null | sort
)

action=$(printf '%s\n' "Select wallpaper" "Add wallpaper file" "Add wallpaper folder" | wofi --dmenu --prompt "Wallpaper manager" --insensitive)
case "$action" in
  "Add wallpaper file") add_file; exec "$0" ;;
  "Add wallpaper folder") add_folder; exec "$0" ;;
  "Select wallpaper") ;;
  *) exit 0 ;;
esac

if ((${#images[@]} == 0)); then
  notify "Add an image or folder first"
  exit 0
fi

selected=$(printf '%s\n' "${images[@]}" | wofi --dmenu --prompt "Wallpaper" --insensitive)
[[ -n "$selected" ]] || exit 0

image="$wallpaper_dir/$selected"
[[ -f "$image" ]] || exit 1

temporary=$(mktemp "${selected_file}.XXXXXX")
printf '%s\n' "$selected" >"$temporary"
mv "$temporary" "$selected_file"

pkill -x swaybg >/dev/null 2>&1 || true
exec swaybg -i "$image" -m fill