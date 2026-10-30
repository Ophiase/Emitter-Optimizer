#!/usr/bin/env bash
# Usage: biome.sh <file>...
# Runs biome in each checkout that owns one of the .js arguments, so a worktree
# lints itself. The scope is biome.json, and the version is the one its
# $schema names, which `biome migrate` keeps in step. Skipped when npx is not
# installed. Exits 1 when biome reports anything.
set -uo pipefail

command -v npx >/dev/null 2>&1 || exit 0

declare -A roots=()
for file in "$@"; do
  [[ -f $file && $file == *.js ]] || continue
  root=$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null) || continue
  [[ -f $root/biome.json ]] && roots[$root]=1
done

report=""
for root in "${!roots[@]}"; do
  version=$(grep -oE 'schemas/[0-9]+\.[0-9]+\.[0-9]+/schema\.json' "$root/biome.json" | cut -d/ -f2)
  if [[ -z $version ]]; then
    report+="$root/biome.json: no versioned \$schema, so no biome version to run"$'\n'
    continue
  fi
  output=$(cd "$root" && npx --yes "@biomejs/biome@$version" check 2>&1) ||
    report+="$output"$'\n'
done

[[ -z $report ]] && exit 0

printf 'biome reported JavaScript violations:\n\n%s\n' "$report"
# shellcheck disable=SC2016  # the backticked command is literal text
printf 'Fix them now: `biome check --write`, at that same version, handles the\nformatting and the safe fixes.\n'
exit 1
