# Comments

How comments are judged in every file of this repository, whatever the
language. [python.md](python.md) adds what is specific to Python.

A comment records a **why** the code cannot express. Anything else is deleted:
a better name, a smaller unit, or the structure itself says it instead.

## The rejected shapes

[comment-slop.sh](../checks/comment-slop.sh) reports these on the lines the
working tree added.

| Shape | What it is |
| --- | --- |
| `HEADER` | A comment block at the top of a file |
| `BANNER` | `# ====`, `# ----`, `# --- Section ---` |
| `STEP` | `# Step 1:`, `# Phase 2`, `# 1) ...` |
| `NARRATIVE` | `# Now we ...`, `# This blocks until ...`, `# Create the client` |
| `VARIABLE` | A one-line comment sitting above an assignment |
| `INLINE` | A trailing comment on an assignment |
| `BLOCK` | Three or more consecutive comment lines |
| `DENSITY` | Five or more comment lines added to one file |
| `REMOTE` | The comment names another file, or a symbol this one never touches |
| `DESCRIPTION` | A Terraform `description` longer than 120 characters |

Tool directives are exempt everywhere: `noqa`, `type:`, `pragma`, `ruff:`,
`fmt:`, `shellcheck`, `eslint`, `prettier`, `yamllint` and the like.

## `REMOTE` is an architecture finding, not a style one

The others say a comment is badly written. This one says the *code* is.

A module is not supposed to justify its own existence. When a comment has to
reach outside the file — name a neighbouring path, a type defined elsewhere,
a constant that must stay in step with another module — it is reporting that
the file handles something that is not local to it. The comment is the
symptom; the coupling is the defect.

So the fix is almost never to reword the comment. It is to ask why the code
needed it: a value that must match another file wants to be imported from one
place rather than described twice, an effect felt at the other end of the
codebase wants to be expressed in a type or a call rather than in prose, a
behaviour that only makes sense next to another module usually belongs in it.

Deleting the comment and leaving the coupling is the one wrong answer. If the
coupling is real and cannot move today, say so in the turn and leave the
comment — that is a decision, not an oversight.

The check is deliberately narrow: a domain word the file happens not to spell
is not a design problem, a neighbour's filename is.

## Which shapes apply where

A profile is chosen from the file extension. The two columns that move are
`HEADER` and the volume caps, because what they forbid is conventional in one
language and slop in another.

| | `.py` | `.yaml` `.yml` | `.just` | `.sh` | `.js` | `.tf` | `.rs` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `BANNER` `STEP` `NARRATIVE` `VARIABLE` `INLINE` `REMOTE` | yes | yes | yes | yes | yes | yes | yes |
| `HEADER` | yes | no | no | no | no | no | no |
| `BLOCK` at | — | 3 lines | 2 lines | 5 lines | 5 lines | 3 lines | 3 lines |
| `DENSITY` at | 5, as a note | 5 | 3 | 10 | 10 | 5 | 5 |
| `DESCRIPTION` | — | — | — | — | — | yes | — |

In Rust, `///` and `//!` are documentation, not comments: they are judged by
[rust.md](rust.md), and only `//` lines count here.

`HEADER` is Python's alone because Python has somewhere better to put it: a
module docstring, which the same hook caps at three lines. Elsewhere the cap
on a leading block is `BLOCK`, with one exception — a `.sh` or `.js` file may
open with a header of any length, since that is how a reader learns what the
file is for before reading any of it.

Python has no `BLOCK` and only a soft `DENSITY` note because its own shapes
already catch what they would: a comment there sits above an assignment or
opens a file, and both are named. The caps exist for the formats where a
comment can sit anywhere, and where the failure is the wall of prose rather
than its shape.

## YAML is the one that matters most

A pipeline or a compose file is read by a human under pressure, looking for
one value. Every comment line pushes the thing they came for further down the
screen. So the bar is higher than elsewhere, not lower:

- Prefer a name. A key, an anchor or a file split says more than a sentence
  about it, and cannot go stale.
- Two lines is the budget for anything worth keeping. Past that, it belongs in
  a rule or a doc, linked from the file.
- Never restate the key below. `# the broker's port` above `port:` is noise.
- What deserves the budget: a constraint from outside the file — why a value
  cannot be changed, what breaks if it is, which external system imposes it.

## Terraform has `description`, kept to a sentence

A variable's `description` is a comment the tooling prints: it carries the
same weight, so it says what the value is in one sentence. What each field
of an object means, its defaults and its constraints, goes in the module's
README, where a table reads better than a paragraph in a string.

## Justfiles have `[doc]`

What a recipe does goes in `[doc("...")]`, which `just -l` shows to whoever
needs it; a comment above the recipe is read by nobody. That leaves a comment
almost nothing to say, so the budget is one line. A procedure run once — a
data copy, a fix-up — is not a recipe at all: run it, and say so in the PR.

## HTML

Not covered. The templates hold almost no comments today, and the profile
would need a second comment syntax to enforce nothing.
