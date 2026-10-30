# Layout

A folder is a concept, and its entry file (`mod.rs`, `lib.rs`, `main.rs`)
is its door: what the rest of the code may use, re-exported there.

- **Seven entries at most** in a folder of code (`.rs`, `.js`), files and
  folders counted together. Past seven, two concepts share the folder:
  name them and split.
- **Two hundred lines at most** in a file of code, its test module left
  out. A longer file holds several concepts: in Rust, a type's methods may
  be spread over several files, one `impl` block per concern.
- A folder is named after what it holds, never `utils`, `common`, `misc`.
- Moving a file must not change what the rest of the code imports: the
  door re-exports.

[folder-size.sh](../checks/folder-size.sh) and
[file-length.sh](../checks/file-length.sh) check the files changed in the
working tree, so a flat folder or a long file is split the next time it is
touched.

YAML files end in `.yaml`, never `.yml`
([yaml-extension.sh](../checks/yaml-extension.sh)).
