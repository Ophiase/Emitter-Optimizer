#!/usr/bin/env bash
# Usage: sonar-heuristic.sh <file>...
# Reports, on the lines the working tree added to each .py or .js file, the
# findings SonarQube keeps raising that the linters do not: a fast, dumb
# pattern match that runs before the scan does. Exits 1 when it reports
# anything.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

report=""
for file in "$@"; do
  [[ -f $file ]] || continue
  [[ $file == *.py || $file == *.js ]] || continue
  "$checks/is-ignored.sh" sonar-heuristic "$file" && continue
  added=$("$checks/added-lines.sh" "$file")
  [[ -n $added ]] || continue
  if [[ $file == *.py ]]; then
    finding=$(timeout 5 python3 -I "$checks/sonar_heuristic.py" "$file" "$added" 2>/dev/null)
  else
    finding=$(timeout 5 awk -v file="$file" -v added="$added" -f "$checks/sonar-heuristic.awk" "$file")
  fi
  [[ -n $finding ]] && report+="$finding"$'\n'
done

[[ -z $report ]] && exit 0

printf 'Patterns SonarQube reports, in the lines just written:\n\n%s\n' "$report"
printf 'Fix them now: each one comes back as a finding after the merge.\n'
exit 1
