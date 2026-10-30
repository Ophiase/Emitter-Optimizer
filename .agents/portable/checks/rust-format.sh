#!/usr/bin/env bash
# Usage: rust-format.sh <file>...
# Runs rustfmt --check on the Rust files among the arguments; rustfmt finds
# the repository's rustfmt.toml from each file. Skipped when rustfmt is not
# installed. Exits 1 when a file is not formatted.
set -uo pipefail

command -v rustfmt >/dev/null 2>&1 || exit 0

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

files=()
for file in "$@"; do
  [[ -f $file && $file == *.rs ]] || continue
  "$checks/is-ignored.sh" rust-format "$file" && continue
  files+=("$file")
done

((${#files[@]} == 0)) && exit 0

report=$(rustfmt --check --edition 2024 "${files[@]}" 2>&1) && exit 0

printf 'rustfmt would reformat:\n\n%s\n\n' "$report"
# shellcheck disable=SC2016  # the backticked command is literal text
printf 'Run `cargo fmt` in the workspace, then check the result reads well.\n'
exit 1
