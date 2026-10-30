#!/usr/bin/env bash
# Usage: is-ignored.sh <check> <file>
# Exits 0 when <file> matches a pattern of <check>.ignore, in the folder the
# repository names in $CHECKS_CONFIG. A pattern is a bash glob matched against
# the absolute path, one per line; blank lines and # lines are skipped.
set -uo pipefail

[[ -n ${CHECKS_CONFIG:-} && -f $CHECKS_CONFIG/$1.ignore ]] || exit 1

path=$(realpath -m "$2")
while IFS= read -r pattern || [[ -n $pattern ]]; do
  [[ -z $pattern || $pattern == \#* ]] && continue
  # shellcheck disable=SC2053  # the right-hand side is a glob on purpose
  [[ $path == $pattern ]] && exit 0
done <"$CHECKS_CONFIG/$1.ignore"

exit 1
