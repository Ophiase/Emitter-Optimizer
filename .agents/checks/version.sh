#!/usr/bin/env bash
# Usage: version.sh <file>...
# Reports a VERSION that has no section in CHANGELOG.md or differs from
# CITATION.cff, and workspace versions that disagree with each other. Runs
# whatever files it is given.
set -uo pipefail

root=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
version=$(tr -d '[:space:]' <"$root/VERSION")

status=0
if ! grep -q "^## $version " "$root/CHANGELOG.md"; then
  printf 'CHANGELOG.md has no section for %s.\n' "$version"
  status=1
fi

if [[ -f $root/CITATION.cff ]]; then
  citation=$(awk '/^version:/ { print $2; exit }' "$root/CITATION.cff")
  if [[ $version != "$citation" ]]; then
    printf 'VERSION says %s, CITATION.cff says %s: bump both together.\n' "$version" "$citation"
    status=1
  fi
fi

for manifest in "$root"/*/Cargo.toml; do
  awk -v manifest="$manifest" '
    /^\[workspace\.package\]/ { inside = 1; next }
    /^\[package\]/ { inside = 1; next }
    /^\[/ { inside = 0 }
    inside && /^version/ { gsub(/[" ]/, "", $0); split($0, parts, "="); print manifest, parts[2]; exit }
  ' "$manifest"
done | sort -k2,2 -u | awk '
  { seen[$2] = seen[$2] " " $1; count[$2]++ }
  END {
    status = 0
    if (length(seen) > 1) {
      for (version in seen) printf "The workspaces disagree on %s:%s\n", version, seen[version]
      status = 1
    }
    exit status
  }' || status=1

exit $status
