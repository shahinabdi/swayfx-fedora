#!/usr/bin/env bash
set -euo pipefail

config="$HOME/.config/swayfx/config"
choice=$(printf '%s\n' "AZERTY (fr)" "QWERTY (us)" | wofi --dmenu --prompt "Keyboard layout" --insensitive)

case "$choice" in
  "AZERTY (fr)") layout="fr" ;;
  "QWERTY (us)") layout="us" ;;
  *) exit 0 ;;
esac

[[ -f "$config" ]] || exit 1
sed -i -E "s/^    xkb_layout \"[^\"]*\"/    xkb_layout \"$layout\"/" "$config"
swaymsg reload

if command -v notify-send >/dev/null 2>&1; then
  notify-send "Keyboard layout" "Switched to $choice"
fi