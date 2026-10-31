#!/usr/bin/env bash
# Usage: file-length.sh <file>...
# Past 80 lines of code (imports, blanks and comments left out) a Python file
# is flagged as a question; past 200 it fails. Short is the default, not a law.
set -uo pipefail

flag=80
limit=200
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
    printf '%s has %d lines of code, more than %d: it is two concepts, split it.\n' "$file" "$count" "$limit"
    status=1
  elif ((count > flag)); then
    printf 'note: %s has %d lines of code; is it still one concept?\n' "$file" "$count"
  fi
done

exit $status
