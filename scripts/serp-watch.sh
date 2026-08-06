#!/usr/bin/env bash
set -euo pipefail

project_dir="/home/narumi/claude-projects/natobee-hp"
logs_dir="$project_dir/logs"
state_file="$logs_dir/serp-watch.state"

mkdir -p "$logs_dir"

if [[ -f "$state_file" ]] && [[ "$(<"$state_file")" == "done" ]]; then
  exit 0
fi

log_file="$logs_dir/serp-watch-$(date +%Y%m%d-%H%M).log"
screenshot_path="/tmp/serp-watch-$(date +%Y%m%d-%H%M%S).png"
exec >>"$log_file" 2>&1

chrome_started=false

finish() {
  local status=$?
  local chrome_pids=()

  if [[ "$chrome_started" == true ]]; then
    mapfile -t chrome_pids < <(pgrep -f 'google-chrome.*remote-debugging-port=9581' || true)
    if (( ${#chrome_pids[@]} > 0 )); then
      kill "${chrome_pids[@]}" 2>/dev/null || true
    fi
  fi

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

json_result="$(node "$project_dir/scripts/serp-watch.mjs" "$screenshot_path")"
printf '[SERP] %s\n' "$json_result"

title="$(node -e '
  try {
    const value = JSON.parse(process.argv[1]);
    process.stdout.write(typeof value.title === "string" ? value.title : "");
  } catch (error) {
    console.error("[ERROR] Invalid SERP JSON:", error.message);
    process.exit(1);
  }
' "$json_result")"
expected_title="${SERP_EXPECT:-経営者の右腕}"

if [[ "$title" == *"$expected_title"* ]]; then
  notification_body="$(cat <<'EOF'
📂 natobee-hp｜Google検索の表示が新しくなりました

### 前回までのチャットの流れ
1. 検索結果が古いままだとご指摘をいただき、**Googleの取り直しを毎日見張る**ことにしていました。

### 報告
1. Google検索の結果が、**新しいタイトルと説明文**に切り替わりました。
2. 添付は、実際の検索結果をそのまま撮ったものです。

### 相談
1. 特にありません。
EOF
)"

  /home/narumi/.claude/scripts/pm-discord.sh notify "$notification_body" \
    --project natobee-hp \
    --attach "$screenshot_path"

  printf 'done\n' >"$state_file"
  export XDG_RUNTIME_DIR=/run/user/1000
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
  systemctl --user disable --now natobee-serp-watch.timer
  exit 0
fi

echo "[SERP] Expected title text not found; retrying Search Console indexing request."
node "$project_dir/scripts/gsc-reindex.mjs"
exit 0
