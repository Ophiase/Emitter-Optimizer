#!/usr/bin/env bash
# Usage: yaml-extension.sh <file>...
# Reports YAML files named .yml: this project writes .yaml only.
set -uo pipefail

status=0
for file in "$@"; do
  if [[ $file == *.yml ]]; then
    printf '%s: name it .yaml, never .yml.\n' "$file"
    status=1
  fi
done
exit $status
