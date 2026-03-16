#!/usr/bin/env bash
# Claude Code statusLine command — robbyrussell style

input=$(cat)

raw_dir=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
# Collapse HOME to ~, then take basename (robbyrussell shows short dir)
collapsed="${raw_dir/#$HOME/\~}"
dir=$(basename "$collapsed")
# Keep ~ as-is when we are directly in HOME
[ "$collapsed" = "~" ] && dir="~"

model=$(echo "$input" | jq -r '.model.display_name // ""')

used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used" ]; then
  ctx_info=" ctx:${used%.*}%"
else
  ctx_info=""
fi

# Git branch (skip optional lock to avoid blocking)
branch=$(git -C "$raw_dir" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
if [ -n "$branch" ]; then
  git_info=" \033[00;36mgit:(\033[31m${branch}\033[00;36m)\033[00m"
else
  git_info=""
fi

printf "\033[01;32m$(whoami)@$(hostname -s)\033[00m \033[01;34m%s\033[00m%b [\033[00;35m%s\033[00m%s]" \
  "$dir" "$git_info" "$model" "$ctx_info"
