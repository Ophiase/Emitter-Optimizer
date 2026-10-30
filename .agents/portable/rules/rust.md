# Rust

How Rust code in this repository is expected to look. The same taste as
[python.md](python.md), in Rust's own tools; comments follow
[comments.md](comments.md).

## Lints carry the rules

Policy lives once, in the workspace `Cargo.toml` (`[workspace.lints]`), and
every crate opts in with `[lints] workspace = true`:

- `clippy::pedantic` as warnings, and warnings fail the check
  (`cargo clippy --all-targets -- -D warnings`).
- `unwrap_used`, `expect_used`, `panic`, `todo`, `dbg_macro` denied outside
  tests: a library returns errors, it does not abort.
- `min_ident_chars` with no allowed names: no single-letter names, not even
  `i`, `x` or `t`. Write `column`, `along_x`, `travelled`.
- `unsafe_code` forbidden until a measured need says otherwise.
- `too-many-lines-threshold = 40` in `clippy.toml`: a function fits on a
  screen.

`#[expect(lint, reason = "...")]`, never `#[allow]`: the reason is the
review, and the attribute fails once the lint no longer fires.

## Types say what numbers mean

- A primitive with a meaning gets a newtype when mixing two of them must be a
  type error (`WorldPoint` and `VoxelPoint` are both three floats), a type
  alias when it only documents.
- A closed set of choices is an `enum`, never a string or a boolean pair.
- Lossy numeric casts live in a few named functions, each with one
  `#[expect]` and its reason; nowhere else.
- Accept slices and references, return owned immutable data (`Box<[T]>`) or
  iterators. Pass small `Copy` types by value.
- A tuple of more than two fields in a signature is a struct.

## Shape of the code

- Short functions, short files, one concept per file; a directory module when
  a concept has parts.
- Libraries define their errors with `thiserror`; only binaries use `anyhow`.
- Libraries never print; binaries write to locked `stdout` and `stderr`.
- `#[must_use]` on pure functions returning a value.
- A doc comment is for a signature a reader cannot decode on its own — units,
  conventions, edge cases — not for a summary of the code below it.

## Tests

The same bar as [python-remarks.md](python-remarks.md): each test checks a
deterministic algorithmic property, on synthetic data built from constants,
never a value copied from a run. Prefer properties (trilinear sampling is
exact on a linear field) to snapshots.

## Tooling to grow into

`cargo-deny` (licences, advisories, duplicate versions), `cargo-machete` or
`cargo-shear` (unused dependencies), `cargo-nextest` (faster test runner),
`typos`. Add each when the workspace is large enough to need it.
