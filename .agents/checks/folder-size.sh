#!/usr/bin/env bash
# Usage: folder-size.sh <file>...
# Reports each Python folder holding more than seven entries, among the
# folders of the files given. See .agents/rules/layout.md.
set -uo pipefail

limit=7
status=0
declare -A seen=()

for file in "$@"; do
  [[ -f $file && $file == *.py ]] || continue
  case $file in .agents/*) continue ;; esac
  folder=$(dirname "$file")
  [[ -n ${seen[$folder]:-} || ! -d $folder ]] && continue
  seen[$folder]=1
  count=$(find "$folder" -mindepth 1 -maxdepth 1 ! -name '.*' ! -name '__pycache__' | wc -l)
  if ((count > limit)); then
    printf '%s holds %d entries, more than %d: split it into named concepts.\n' "$folder" "$count" "$limit"
    status=1
  fi
done

exit $status
