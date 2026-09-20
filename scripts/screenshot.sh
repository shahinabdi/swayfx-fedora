#!/usr/bin/env bash
set -euo pipefail

directory="${XDG_PICTURES_DIR:-$HOME/Pictures}/Screenshots"
mkdir -p "$directory"
file="$directory/$(date +%Y-%m-%d_%H-%M-%S).png"
case "${1:-full}" in
  full) grim "$file" ;;
  area) grim -g "$(slurp)" "$file" ;;
  *) printf 'Usage: %s [full|area]\n' "$0" >&2; exit 2 ;;
esac
makoctl notify -t 2500 "Screenshot saved" "$file"
