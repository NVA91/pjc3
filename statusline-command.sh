#!/usr/bin/env bash
# Claude Code statusLine command

input=$(cat)

dir=$(echo "$input" | jq -r '
  (.workspace.current_dir // .cwd // "") |
  gsub("^'"$HOME"'"; "~")
')

model=$(echo "$input" | jq -r '.model.display_name // ""')

used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used" ]; then
  ctx_info=" | ctx: ${used%.*}%"
else
  ctx_info=""
fi

printf "\033[01;32mubhp-nova@nova\033[00m:\033[01;34m%s\033[00m [%s%s]" \
  "$dir" "$model" "$ctx_info"
