#!/usr/bin/env bash
# Usage: changed-files.sh
# Lists, relative to the repository root, the files the working tree changed
# since HEAD plus the untracked ones. Deletions are left out: a check handed a
# missing path may abandon the whole run.
set -uo pipefail

cd "$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1

{
  git diff --name-only --diff-filter=d HEAD
  git diff --cached --name-only --diff-filter=d
  git ls-files --others --exclude-standard
} 2>/dev/null | sort -u
