#!/usr/bin/env bash
# Usage: portable.sh <file>...
# Reports the files under .agents/portable/ that name something only this
# project has. That folder is copied as is into other repositories, so it may
# not know this one. Exits 1 when it reports anything.
set -uo pipefail

portable=$(realpath "$(dirname "${BASH_SOURCE[0]}")/../portable")

markers='phenomena|quasi-qual|lexicon|ideas/'
markers="$markers|\\.agents/(rules|checks)/"

report=""
for file in "$@"; do
  [[ -f $file && $(realpath "$file") == "$portable"/* ]] || continue
  hits=$(grep -nEi "$markers" "$file")
  [[ -n $hits ]] && report+=$(printf '%s\n' "$hits" | sed "s|^|$file:|")$'\n'
done

[[ -z $report ]] && exit 0

printf 'Project-specific reference in .agents/portable:\n\n%s\n' "$report"
cat <<'EOF'
Everything in .agents/portable must hold in any repository. Move the
project-specific part to .agents/rules/ or .agents/checks/, which may extend
a portable file but never the other way round.
EOF
exit 1
