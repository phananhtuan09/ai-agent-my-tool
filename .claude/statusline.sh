#!/usr/bin/env bash

input=$(cat)

parse_json() {
  local key="$1"
  local fallback="$2"
  local result=""

  if command -v jq >/dev/null 2>&1; then
    result=$(echo "$input" | jq -r "$key // empty" 2>/dev/null)
  elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    local py_cmd="python3"
    command -v python3 >/dev/null 2>&1 || py_cmd="python"
    local py_key="${key#.}"  # strip leading dot
    result=$(echo "$input" | $py_cmd -c "
import sys, json
try:
    data = json.load(sys.stdin)
    keys = '${py_key}'.split('.')
    val = data
    for k in keys:
        if k and isinstance(val, dict):
            val = val.get(k)
        else:
            val = None
    if val is not None:
        print(val)
except:
    pass
" 2>/dev/null)
  fi

  echo "${result:-$fallback}"
}

model=$(parse_json '.model.display_name' "Unknown")
current_dir=$(parse_json '.workspace.current_dir' "")
used_pct=$(parse_json '.context_window.used_percentage' "")

# Normalize Windows backslashes to forward slashes
current_dir="${current_dir//\\//}"

if [ -n "$current_dir" ]; then
  folder=$(basename "$current_dir")
else
  folder=$(basename "$PWD")
fi

branch=""
if [ -n "$current_dir" ] && ([ -d "$current_dir/.git" ] || git -C "$current_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1); then
  branch=$(git -C "$current_dir" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

output="[$model] 📁 $folder"

if [ -n "$branch" ]; then
  output="$output | 🌿 $branch"
fi

if [ -n "$used_pct" ]; then
  printf_pct=$(printf "%.0f" "$used_pct" 2>/dev/null || echo "$used_pct")
  output="$output | ctx ${printf_pct}%"
fi

echo "$output"
