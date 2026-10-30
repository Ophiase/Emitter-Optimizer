#!/usr/bin/env bash
# Usage: french.sh <file>...
# Flags French prose outside the places french.ignore sanctions. French
# anywhere else is an automatic blocker (AGENTS.md), so this is a heuristic
# tripwire: a file needs two distinct high-precision markers before it is
# reported, and the reader confirms the hit before rewriting. Exits 1 when it reports anything.
set -uo pipefail

markers="c'est|n'est|qu'il|qu'elle|d'un|d'une|l'on|s'il|jusqu'|aujourd'hui"
markers="$markers|être|était|étaient|peut|peuvent|faut|cette|celui|celle"
markers="$markers|également|toujours|lorsque|pourquoi|puisque|ainsi|afin"
markers="$markers|plusieurs|beaucoup|chaque|voici|permet|permettre"

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
self=$(realpath "${BASH_SOURCE[0]}")

report=""
for file in "$@"; do
  [[ -f $file ]] || continue
  [[ $(realpath "$file") == "$self" ]] && continue
  "$checks/is-ignored.sh" french "$file" && continue
  file "$file" | grep -qi 'text\|json\|empty' || continue
  hits=$(grep -oEi "\\b($markers)" "$file" 2>/dev/null | tr '[:upper:]' '[:lower:]' | sort -u)
  (($(printf '%s' "$hits" | grep -c .) < 2)) && continue
  report+="$file: $(printf '%s' "$hits" | tr '\n' ' ')"$'\n'
done

[[ -z $report ]] && exit 0

printf 'Possible French text (English-only is a blocker):\n\n%s\n' "$report"
printf 'Read each file: rewrite the French in English, or say so if this is a false positive.\n'
exit 1
