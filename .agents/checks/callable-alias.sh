#!/usr/bin/env bash
# Usage: callable-alias.sh <file>...
# Prints a note for every `Callable`, so a callback can become a Protocol with
# __call__ and a name a reader finds by autocomplete.
set -uo pipefail

for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  while IFS= read -r line; do
    printf 'note: %s:%s: Callable is a function shape; a Protocol with __call__ names the role.\n' "$file" "$line"
  done < <(grep -nE '\bCallable\b' "$file" || true)
done

exit 0
