#!/usr/bin/env bash
# Usage: version.sh <file>...
# Reports a VERSION that disagrees with pyproject.toml, the package, CITATION.cff
# or the sections of CHANGELOG.md. Runs whatever files it is given.
set -uo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
version=$(tr -d '[:space:]' <"$root/VERSION")
status=0

report() {
  printf '%s says %s, VERSION says %s: bump both together.\n' "$1" "$2" "$version"
  status=1
}

manifest=$(awk '/^\[project\]/ { inside = 1; next } /^\[/ { inside = 0 } inside && /^version/ { gsub(/[",]/, "", $0); sub(/^version = /, "", $0); print; exit }' "$root/pyproject.toml")
[[ -z $manifest || $manifest == "$version" ]] || report pyproject.toml "$manifest"

package=$(awk -F'"' '/^__version__/ { print $2; exit }' "$root/src/emitter_optimizer/__init__.py")
[[ -z $package || $package == "$version" ]] || report src/emitter_optimizer/__init__.py "$package"

if [[ -f $root/CITATION.cff ]]; then
  citation=$(awk '/^version:/ { print $2; exit }' "$root/CITATION.cff")
  [[ $citation == "$version" ]] || report CITATION.cff "$citation"
fi

if ! grep -q "^## $version " "$root/CHANGELOG.md"; then
  printf 'CHANGELOG.md has no section for %s.\n' "$version"
  status=1
fi

exit $status
