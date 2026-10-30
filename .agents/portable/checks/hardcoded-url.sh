#!/usr/bin/env bash
# Usage: hardcoded-url.sh <file>...
# Reports the URLs the working tree added to each .py or .js file. A URL stays
# when its line carries a `hardcoded-url: <reason>` directive, which is what
# the developer reviews. Exits 1 when it reports anything.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

report=""
for file in "$@"; do
  [[ -f $file ]] || continue
  [[ $file == *.py || $file == *.js ]] || continue
  "$checks/is-ignored.sh" hardcoded-url "$file" && continue
  added=$("$checks/added-lines.sh" "$file")
  [[ -n $added ]] || continue
  finding=$(awk -v file="$file" -v added="$added" -f "$checks/hardcoded-url.awk" "$file")
  [[ -n $finding ]] && report+="$finding"$'\n'
done

[[ -z $report ]] && exit 0

rules=$(realpath --relative-to="$PWD" "$checks/../rules")
printf 'Hardcoded URL in the lines just written:\n\n%s\n' "$report"
printf 'A URL in code is an address someone has to find and change by hand\n'
printf '(%s/urls.md). Take it out: read it from the typed config, let a\n' "$rules"
cat <<'EOF'
fake own the transport, or build it from what the caller already holds.
Hiding it (an f-string scheme, httpx.URL(scheme=...)) is the same URL.

If none of that works, keep it with `# hardcoded-url: <why>` on the line,
three words at least, and tell the developer which one you kept and why —
they decide.
EOF
exit 1
