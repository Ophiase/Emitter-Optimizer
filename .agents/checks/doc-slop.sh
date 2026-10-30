#!/usr/bin/env bash
# Usage: doc-slop.sh <file>...
# Reports Rust doc comments that only repeat the name they document. A doc
# says what the signature cannot: units, conventions, edge cases.
set -uo pipefail

checks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
status=0
for file in "$@"; do
  [[ -f $file && $file == *.rs ]] || continue
  gawk -f "$checks/doc-slop.awk" "$file" || status=1
done
exit $status
