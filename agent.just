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
    git ls-files -- '*.py' ':!tests/*' ':!.agents/*' | while IFS= read -r file; do
        [[ -f $file ]] || continue
        awk 'END { print NR + 0 }' "$file" | sed "s|\$| $file|"
    done | sort -rn | head -n "$1" | while read -r lines file; do
        if ((lines > 200)); then colour=31; elif ((lines > 100)); then colour=33; else colour=32; fi
        printf '\e[%sm%5d\e[0m  %s\n' "$colour" "$lines" "$file"
    done

[group("code")]
[doc("Files carrying many functions and classes: just agent::shapes 20; red past 10 functions or 3 classes")]
[script("bash")]
shapes count="20":
    set -euo pipefail
    [[ $1 =~ ^[0-9]+$ ]] || { echo "a count of files" >&2; exit 1; }
    git ls-files -- '*.py' ':!tests/*' ':!.agents/*' | while IFS= read -r file; do
        [[ -f $file ]] || continue
        functions=$(grep -cE '^[[:space:]]*def ' "$file" || true)
        classes=$(grep -cE '^[[:space:]]*class ' "$file" || true)
        lines=$(wc -l < "$file")
        printf '%4d %4d %5d %s\n' "$functions" "$classes" "$lines" "$file"
    done | sort -k1,1nr -k2,2nr | head -n "$1" | while read -r functions classes lines file; do
        if ((functions > 10 || classes > 3)); then colour=31; elif ((functions > 6 || classes > 1)); then colour=33; else colour=32; fi
        printf '\e[%sm%3d f %2d c %5d l\e[0m  %s\n' "$colour" "$functions" "$classes" "$lines" "$file"
    done

service_url := env("EMITTER_URL", "http://127.0.0.1:8765")

[group("service")]
[doc("Serve the engine on 127.0.0.1, in the foreground; run it in a background shell")]
[script("bash")]
serve *arguments:
    set -euo pipefail
    exec uv run python -m emitter_optimizer serve "$@"

[group("service")]
[doc("Where the service answers; EMITTER_URL overrides the default")]
url:
    @printf '%s\n' "{{ service_url }}"

[group("service")]
[doc("The whole state, as JSON: positions, gain, history, seed")]
state:
    @curl -sS --fail-with-body --max-time 30 "{{ service_url }}/api/state"

[group("service")]
[doc("The state through a jq filter: just agent::query '.gain'")]
[script("bash")]
query filter:
    set -euo pipefail
    curl -sS --fail-with-body --max-time 30 "{{ service_url }}/api/state" | jq "$1"

[group("service")]
[doc("Run the descent: just agent::run 100 0 (iterations, seed)")]
[script("bash")]
run iterations="50" seed="0":
    set -euo pipefail
    [[ $1 =~ ^[0-9]+$ ]] || { echo "iterations: a non-negative integer" >&2; exit 1; }
    [[ $2 =~ ^[0-9]+$ ]] || { echo "seed: a non-negative integer" >&2; exit 1; }
    curl -sS --fail-with-body --max-time 600 -X POST \
        -H 'Content-Type: application/json' \
        --data-binary "$(jq -cn --argjson iterations "$1" --argjson seed "$2" '{iterations: $iterations, seed: $seed}')" \
        "{{ service_url }}/api/run"

[group("service")]
[doc("Draw emitters from a seed: just agent::place 12 0")]
[script("bash")]
place emitters="12" seed="0":
    set -euo pipefail
    [[ $1 =~ ^[0-9]+$ ]] || { echo "emitters: a non-negative integer" >&2; exit 1; }
    [[ $2 =~ ^[0-9]+$ ]] || { echo "seed: a non-negative integer" >&2; exit 1; }
    curl -sS --fail-with-body --max-time 60 -X POST \
        -H 'Content-Type: application/json' \
        --data-binary "$(jq -cn --argjson emitters "$1" --argjson seed "$2" '{emitters: $emitters, seed: $seed}')" \
        "{{ service_url }}/api/place"

[group("service")]
[doc("Stop the running descent")]
stop:
    @curl -sS --fail-with-body --max-time 30 -X POST -H 'Content-Type: application/json' --data-binary '{}' "{{ service_url }}/api/stop"

[group("service")]
[doc("Save the current figure: just agent::figure out/figure.png")]
[script("bash")]
figure out="out/figure.png":
    set -euo pipefail
    mkdir -p "$(dirname "$1")"
    curl -sS --fail-with-body --max-time 60 "{{ service_url }}/api/figure.png" -o "$1"
    echo "$1"

[group("service")]
[doc("Save the state: just agent::save out/state.json")]
[script("bash")]
save out="out/state.json":
    set -euo pipefail
    mkdir -p "$(dirname "$1")"
    curl -sS --fail-with-body --max-time 60 "{{ service_url }}/api/export" -o "$1"
    echo "$1"

[group("code")]
[doc("The 2024 shapes still in the code, counted per pattern; non-zero exit while any remain")]
[script("bash")]
smells:
    set -euo pipefail
    patterns=('tuple\[int, int\]' 'tuple\[float, float\]' 'matplotlib' 'cv2' 'MapType' 'def set_' 'is_aborting' 'NotImplementedError' 'from_mapping' 'derivative')
    total=0
    for pattern in "${patterns[@]}"; do
        count=$(git grep -cE "$pattern" -- src scripts settings | awk -F: '{ sum += $2 } END { print sum + 0 }')
        total=$((total + count))
        printf '%5d  %s\n' "$count" "$pattern"
    done
    printf '%5d  total\n' "$total"
    ((total == 0))
