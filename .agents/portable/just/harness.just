[group("gate")]
[doc("Everything that must pass before declaring work done: check, then guards.")]
[script("bash")]
gate:
    set -euo pipefail
    just check
    just guards

[group("setup")]
[doc("Run the project's checks on every commit: git config core.hooksPath .githooks")]
install-hooks:
    git config core.hooksPath .githooks

[group("gate")]
[doc("Branch, last commit and working tree: what a review reads first.")]
status:
    @git branch --show-current
    @git log --oneline -1
    @git status --short

[group("gate")]
[doc("What changed since main, then the working tree.")]
[script("bash")]
brief:
    set -euo pipefail
    git --no-pager diff main...HEAD --stat
    git status --short
