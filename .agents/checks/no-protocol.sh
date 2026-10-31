#!/usr/bin/env bash
# Usage: no-protocol.sh <file>...
# Reports `Protocol` in Python sources: an is-a hierarchy is an ABC, and a
# Protocol hides which implementation is expected (.agents/rules/python.md).
set -uo pipefail

status=0
for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  hits=$(grep -nE '\bProtocol\b' "$file" || true)
  if [[ -n $hits ]]; then
    printf '%s\n' "$hits" | sed "s|^|$file:|"
    status=1
  fi
done

exit $status
