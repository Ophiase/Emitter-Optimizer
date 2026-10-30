set positional-arguments := true

import ".agents/portable/just/harness.just"

[group("gate")]
[doc("The full local gate: lint, types, tests, the guards and the markdown.")]
[script("bash")]
ci:
    set -euo pipefail
    just check
    just guards

[group("code")]
[doc("The longest files of Python, tests left out: just agent::longest 30; green to 100 lines, yellow to 200, red past")]
[script("bash")]
longest count="30":
    set -euo pipefail
    [[ $1 =~ ^[0-9]+$ ]] || { echo "a count of files" >&2; exit 1; }
    git ls-files -- '*.py' ':!tests/*' | while read -r file; do
        awk 'END { print NR + 0 }' "$file" | sed "s|\$| $file|"
    done | sort -rn | head -n "$1" | while read -r lines file; do
        if ((lines > 200)); then colour=31; elif ((lines > 100)); then colour=33; else colour=32; fi
        printf '\e[%sm%5d\e[0m  %s\n' "$colour" "$lines" "$file"
    done
