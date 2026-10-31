#!/usr/bin/env bash
# Usage: no-protocol.sh <file>...
# A Protocol is allowed for a callable role: the class declares __call__.
# Any other Protocol is an is-a hierarchy, and an is-a hierarchy is an ABC.
set -uo pipefail

status=0
for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  if grep -qE '\bProtocol\b' "$file" && ! grep -qE 'def __call__' "$file"; then
    printf '%s: a Protocol must be a callable role; use an ABC for an is-a hierarchy.\n' "$file"
    status=1
  fi
done

exit $status
