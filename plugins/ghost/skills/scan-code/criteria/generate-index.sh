#!/usr/bin/env bash
# Generates criteria/index.yaml from the top-level keys of each criteria YAML.
# Run from the scan-code directory: bash criteria/generate-index.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$SCRIPT_DIR/index.yaml"

echo "# Auto-generated — do not edit. Run: bash criteria/generate-index.sh" > "$OUT"

for file in "$SCRIPT_DIR"/{backend,frontend,mobile}.yaml; do
  name="$(basename "$file" .yaml)"
  echo "${name}:" >> "$OUT"
  # Extract top-level keys (lines that start with a word char and end with colon, no leading spaces)
  grep -E '^[a-z_]+:' "$file" | sed 's/:.*//' | while read -r agent; do
    echo "  - ${agent}" >> "$OUT"
  done
done

echo "Wrote $OUT"
