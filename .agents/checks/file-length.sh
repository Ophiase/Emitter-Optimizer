#!/usr/bin/env bash
# Usage: file-length.sh <file>...
# Reports each Python file longer than 80 lines of code, imports, blanks and
# comments left out: past that it holds several things (rules/python.md).
set -uo pipefail

limit=80
status=0

for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  count=$(awk '
    /^[[:space:]]*(import|from)[[:space:]]/ {
      if ($0 ~ /\($/) in_import = 1
      next
    }
    in_import {
      if ($0 ~ /\)/) in_import = 0
      next
    }
    /^[[:space:]]*$/ { next }
    /^[[:space:]]*#/ { next }
    { lines++ }
    END { print lines + 0 }
  ' "$file")
  if ((count > limit)); then
    printf '%s has %d lines of code, more than %d: split it by concept.\n' "$file" "$count" "$limit"
    status=1
  fi
done

exit $status
