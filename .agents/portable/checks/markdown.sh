#!/usr/bin/env bash
# Usage: markdown.sh <file>...
# Runs rumdl on the markdown files among the arguments; what it skips is the
# exclude list of the repository's rumdl configuration. Skipped when rumdl is
# not installed. Exits 1 when rumdl reports anything.
set -uo pipefail

command -v rumdl >/dev/null 2>&1 || exit 0

files=()
for file in "$@"; do
  [[ -f $file && $file == *.md ]] && files+=("$file")
done

((${#files[@]} == 0)) && exit 0

report=$(rumdl check "${files[@]}" 2>&1) && exit 0

printf 'rumdl reported markdown violations:\n\n%s\n\n' "$report"
# shellcheck disable=SC2016  # the backticked command is literal text
printf 'Fix them now (`rumdl fmt` handles the formatting ones).\n'
exit 1
