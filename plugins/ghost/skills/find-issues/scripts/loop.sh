#!/bin/bash
set -euo pipefail

scan_dir="$1"
prompt="$2"
extra_inputs="${3:-}"
skill_dir="$(cd "$(dirname "$0")/.." && pwd)"

while true; do
  echo "Running $prompt..."
  result=$(claude -p "Read and follow $skill_dir/prompts/$prompt.

## Inputs
- scan_dir: $scan_dir
- skill_dir: $skill_dir
$extra_inputs" \
    --allowedTools 'Read,Write,Edit,Glob,Grep,Bash(mkdir:*)')

  summary=$(echo "$result" | grep -v 'GHOST_COMPLETE' | tail -1 || true)
  if [ -n "$summary" ]; then echo "$summary"; fi

  if echo "$result" | grep -q 'GHOST_COMPLETE'; then
    break
  fi
done
