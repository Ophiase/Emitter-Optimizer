#!/usr/bin/env bash
# Usage: no-suppression.sh <file>...
# Reports `noqa`, `type: ignore` and `ruff: ignore` in Python sources: a
# suppression is a rule the reader cannot see. Fix the code, or declare the
# exception in ruff.toml with the reason it exists.
set -uo pipefail

status=0
for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  hits=$(grep -nE '# *(noqa|type: *ignore|ruff: *ignore)' "$file") || true
  if [[ -n $hits ]]; then
    printf '%s\n' "$hits" | sed "s|^|$file:|"
    status=1
  fi
done

exit $status
