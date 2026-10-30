#!/usr/bin/env bash
# Usage: added-lines.sh <file>
# Prints the line numbers the working tree added to <file> since HEAD, or
# since $ADDED_SINCE when set (a branch's base, to judge committed work), comma
# separated, or ALL for a file git does not track yet. The repository is the
# one that owns <file>, so a worktree answers for itself.
set -uo pipefail

file=$(realpath "$1")
root=$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null) || exit 0

if ! git -C "$root" ls-files --error-unmatch "$file" >/dev/null 2>&1; then
  printf ALL
  exit 0
fi

git -C "$root" diff -U0 --no-color --no-renames "${ADDED_SINCE:-HEAD}" -- "$file" 2>/dev/null |
  awk '/^@@/ {
    if (match($0, /\+[0-9]+(,[0-9]+)?/)) {
      span = substr($0, RSTART + 1, RLENGTH - 1)
      parts = split(span, bounds, ",")
      start = bounds[1] + 0
      count = (parts > 1) ? bounds[2] + 0 : 1
      for (offset = 0; offset < count; offset++) printf "%d,", start + offset
    }
  }'
