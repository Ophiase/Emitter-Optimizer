#!/usr/bin/env bash
# Usage: comment-slop.sh <file>...
# Reports the comment shapes that ../rules/comments.md rejects, on the
# lines the working tree added to each file. Files of another format are
# skipped. Exits 1 when it reports anything.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

syntax_for() {
  case $1 in
    *.py) printf python ;;
    *.yaml | *.yml) printf yaml ;;
    *.just | justfile | */justfile) printf just ;;
    *.sh) printf shell ;;
    *.js) printf javascript ;;
    *.tf) printf terraform ;;
    *.rs) printf rust ;;
  esac
}

report=""
for file in "$@"; do
  [[ -f $file ]] || continue
  syntax=$(syntax_for "$file")
  [[ -n $syntax ]] || continue
  "$checks/is-ignored.sh" comment-slop "$file" && continue
  added=$("$checks/added-lines.sh" "$file")
  [[ -n $added ]] || continue
  finding=$(awk -v file="$file" -v added="$added" -v syntax="$syntax" \
    -f "$checks/comment-slop.awk" "$file")
  [[ -n $finding ]] && report+="$finding"$'\n'
done

[[ -z $report ]] && exit 0

rules=$(realpath --relative-to="$PWD" "$checks/../rules")
printf 'Comment slop in the lines just written:\n\n%s\n' "$report"
printf 'Comments are the exception in this codebase (%s/comments.md, and\n' "$rules"
cat <<'EOF'
python.md for Python). Delete these, or make the code say what the comment
said — a better name, a smaller unit, the structure itself. Keep one only if
it records a *why* the code cannot express, and say out loud which one you
kept and why.

A REMOTE finding is about the code, not the comment: this file is explaining
something that is not local to it. Fix the coupling, or say why it cannot
move — deleting the comment and leaving it is the one wrong answer.
EOF
exit 1
