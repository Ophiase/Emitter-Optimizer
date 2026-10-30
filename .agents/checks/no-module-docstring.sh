#!/usr/bin/env bash
# Usage: no-module-docstring.sh <file>...
# Reports a Python file whose first statement is a string: that is a header,
# and the file name already says it (.agents/rules/python.md).
set -uo pipefail

status=0
for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  first=$(head -n 1 "$file")
  if [[ $first == '\"\"\"'* || $first == "'''"* ]]; then
    printf '%s:1: a module docstring is a header; delete it, or move the why to the function it serves\n' "$file"
    status=1
  fi
done

exit $status
