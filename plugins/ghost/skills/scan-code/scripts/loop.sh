#!/usr/bin/env bash
set -euo pipefail

scan_dir="$1"
prompt="$2"
extra_inputs="${3:-}"
max_parallel="${4:-1}"
cache_dir="${5:-}"
skill_dir="$(cd "$(dirname "$0")/.." && pwd)"

run_one() {
  local work_item="$1"
  local inputs="- scan_dir: $scan_dir
- skill_dir: $skill_dir
- cache_dir: $cache_dir"
  if [ -n "$work_item" ]; then
    inputs="$inputs
- work_item: $work_item"
  fi
  if [ -n "$extra_inputs" ]; then
    inputs="$inputs
$extra_inputs"
  fi

  unset CLAUDECODE
  claude -p "Read and follow $skill_dir/prompts/$prompt.

## Inputs
$inputs" \
    --allowedTools 'Read,Write,Edit,Glob,Grep,Bash(mkdir:*)'
}

get_items() {
  case "$prompt" in
    nominator.md)
      grep '^- \[ \]' "$scan_dir/nominations.md" 2>/dev/null || true
      ;;
    analyzer.md)
      grep '^- \[ \]' "$scan_dir/analyses.md" 2>/dev/null || true
      ;;
    verifier.md)
      grep -rl '\*\*Status\*\*: unverified' "$scan_dir/findings/" 2>/dev/null \
        | while read -r f; do basename "$f"; done || true
      ;;
    *)
      echo "__SINGLE_RUN__"
      ;;
  esac
}

print_summary() {
  local result="$1"
  local summary
  summary=$(echo "$result" | grep -v 'GHOST_COMPLETE' | tail -n 1 || true)
  if [ -n "$summary" ]; then echo "  $summary"; fi
}

# Single-run prompts (planner)
items=$(get_items)
if [ "$items" = "__SINGLE_RUN__" ]; then
  echo "Running $prompt..."
  result=$(run_one "")
  print_summary "$result"
  exit 0
fi

# Parallel loop
while true; do
  items=$(get_items)
  if [ -z "$items" ]; then break; fi

  batch=$(echo "$items" | head -n "$max_parallel")
  count=$(echo "$batch" | wc -l | tr -d ' ')
  echo "Dispatching $count worker(s) for $prompt..."

  pids=()
  tmpfiles=()
  while IFS= read -r item; do
    tmpfile=$(mktemp)
    tmpfiles+=("$tmpfile")
    run_one "$item" > "$tmpfile" 2>&1 &
    pids+=($!)
  done <<< "$batch"

  for i in "${!pids[@]}"; do
    wait "${pids[$i]}" || true
    print_summary "$(cat "${tmpfiles[$i]}")"
    rm -f "${tmpfiles[$i]}"
  done
done

echo "All items completed."