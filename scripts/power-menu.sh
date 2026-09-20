#!/usr/bin/env bash
set -euo pipefail

choice=$(printf 'Lock\nLogout\nSuspend\nReboot\nShutdown' | wofi --dmenu --prompt 'Power')
case "$choice" in
  Lock) swaylock -f -c 0b111a ;;
  Logout) swaymsg exit ;;
  Suspend) systemctl suspend ;;
  Reboot) systemctl reboot ;;
  Shutdown) systemctl poweroff ;;
esac
