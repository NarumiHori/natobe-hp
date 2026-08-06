#!/usr/bin/env bash
# クイックトンネルのURLが変わった時だけ、新しいリンクをDiscordへ通知する。
# 初回は設置担当者が案内するため、URLの保存だけを行う。
set -uo pipefail

METRICS="http://127.0.0.1:20242/quicktunnel"
STATE="$HOME/.claude/.pm-discord/natobee-hp-tunnel-url.txt"
DISCORD="$HOME/.claude/scripts/pm-discord.sh"

mkdir -p "$(dirname "$STATE")"

host=$(curl -s --max-time 5 "$METRICS" | sed -n 's/.*"hostname":"\([^"]*\)".*/\1/p')
[ -z "$host" ] && exit 0   # 起動直後などURLが取れない時は何もしない

url="https://${host}"
prev=$(cat "$STATE" 2>/dev/null || true)
[ "$url" = "$prev" ] && exit 0

printf '%s\n' "$url" > "$STATE"
[ -z "$prev" ] && exit 0   # 初回は保存だけ行い通知しない

"$DISCORD" notify --project natobee-hp "📂 natobee-hp｜テストサイトのリンクが変わりました（トンネル再接続のため）

新しいリンク → ${url}
古いリンクはもう開きません。"
