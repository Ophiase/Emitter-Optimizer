#!/usr/bin/env bash
# Usage: run.sh <check> <file>...
# Runs the named check from this project's checks, or else from the portable
# ones, with the remaining arguments, and exits with its status. A portable
# check reads this project's settings for it (<check>.ignore) from this folder,
# through $CHECKS_CONFIG. An unknown name exits 1, so a misspelt hook reports
# instead of passing silently.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export CHECKS_CONFIG=$checks
name=$1
shift

for script in "$checks/$name.sh" "$checks/../portable/checks/$name.sh"; do
  [[ -x $script ]] && exec "$script" "$@"
done

printf 'No check named %s in %s or its portable checks.\n' "$name" "$checks"
exit 1
