#!/usr/bin/env bash
# Usage: file-length.sh <file>...
# Reports each Python file longer than 200 lines: past that, it holds more
# than one concept. See .agents/rules/layout.md.
set -uo pipefail

limit=200
status=0

for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  count=$(wc -l <"$file")
  if ((count > limit)); then
    printf '%s has %d lines of code, more than %d: split it by concept.\n' "$file" "$count" "$limit"
    status=1
  fi
done

exit $status
