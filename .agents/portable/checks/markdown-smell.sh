#!/usr/bin/env bash
# Usage: markdown-smell.sh <file>...
# Reports the shapes of a hard-to-scan document among the lines the working
# tree added to each .md file: a long paragraph or list item, an ASCII drawing,
# a mermaid block a renderer will not draw, and a file past 200 lines that
# grew. See ../rules/markdown.md. Exits 1 when it reports anything.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
limit=200

text_lines() {
  awk '/^[ \t]*(```|~~~)/ { fenced = !fenced; next } !fenced && NF { count++ } END { print count + 0 }'
}

report=""
for file in "$@"; do
  [[ -f $file && $file == *.md ]] || continue
  "$checks/is-ignored.sh" markdown-smell "$file" && continue
  added=$("$checks/added-lines.sh" "$file")
  [[ -n $added ]] || continue
  finding=$(awk -v file="$file" -v added="$added" -f "$checks/markdown-smell.awk" "$file")
  [[ -n $finding ]] && report+="$finding"$'\n'
  finding=$(timeout 5 python3 -I "$checks/mermaid_crossings.py" "$file" "$added" 2>/dev/null)
  [[ -n $finding ]] && report+="$finding"$'\n'
  lines_now=$(text_lines <"$file")
  lines_before=$(git -C "$(dirname "$file")" show "${ADDED_SINCE:-HEAD}:./$(basename "$file")" 2>/dev/null | text_lines)
  if ((lines_now > limit && lines_now > lines_before)); then
    report+="$file: [LENGTH] $lines_before -> $lines_now lines of text, past $limit; split it or open it with a map"$'\n'
  fi
done

[[ -z $report ]] && exit 0

printf 'Markdown smell in the lines just written:\n\n%s\n' "$report"
cat <<'EOF'
A reader scans before reading. Turn the prose into bullets, a table or a
diagram (markdown.md says which). Keep a long block only when nothing else
carries it, and say so to the developer.
EOF
exit 1
