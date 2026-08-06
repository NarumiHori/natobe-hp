#!/usr/bin/env bash
set -euo pipefail

logs_dir="/home/narumi/claude-projects/natobee-hp/logs"
mkdir -p "$logs_dir"
log_file="$logs_dir/gsc-reindex-$(date +%Y%m%d-%H%M).log"

# Preserve the caller's stdout so the final result can still be shown there.
exec 3>&1
exec >>"$log_file" 2>&1

chrome_started=false

finish() {
  local status=$?

  if [[ "$chrome_started" == true ]]; then
    pkill -f "remote-debugging-port=9581" || true
  fi

  tail -n 1 "$log_file" >&3 || true
  exit "$status"
}
trap finish EXIT

export DISPLAY=:99

if ! pgrep -f 'Xvfb :99' >/dev/null; then
  Xvfb :99 -screen 0 1920x1080x24 &
  sleep 3
fi

if ! pgrep -f 'google-chrome.*remote-debugging-port=9581' >/dev/null; then
  setsid env DISPLAY=:99 google-chrome \
    --user-data-dir=/home/narumi/.claude/browser-profiles/natobee-cfdep \
    --remote-debugging-port=9581 \
    --remote-allow-origins='*' \
    --window-size=1440,900 \
    --no-first-run \
    --no-default-browser-check \
    --disable-features=Translate \
    about:blank >/dev/null 2>&1 &
  chrome_started=true
  sleep 6
fi

node /home/narumi/claude-projects/natobee-hp/scripts/gsc-reindex.mjs
