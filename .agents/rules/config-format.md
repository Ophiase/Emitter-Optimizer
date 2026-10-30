# Configuration files

A configuration file is read by someone looking for one value. Indentation
is how they find it: nesting shows on the page, not inside braces.

- **YAML**: block style. A flow list stays only for a few short scalars on
  one line (`[/proprium, /diaphane]`); a mapping, or a list of mappings, is
  always written as a block.
- **TOML**: `taplo fmt`, with [taplo.toml](../../taplo.toml): an array that
  does not fit is expanded, one item per line, and never collapsed back.
- **Nix**: `nixfmt` (the RFC 166 style): an argument set or a list of more
  than two items goes one per line.
- **JSON**: two spaces, one key per line, as `jq .` writes it.

[config-format.sh](../checks/config-format.sh) checks the first three; the
formatters come with `nix develop`.
