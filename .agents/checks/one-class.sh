#!/usr/bin/env bash
# Usage: one-class.sh <file>...
# Reports a Python file that declares more than one class: a file is one
# concept, and two classes are two concepts (.agents/rules/python.md).
set -uo pipefail

status=0
for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  count=$(grep -cE '^class ' "$file" || true)
  if ((count > 1)); then
    printf '%s: %d classes; one class per file, split it by concept.\n' "$file" "$count"
    status=1
  fi
done

exit $status
