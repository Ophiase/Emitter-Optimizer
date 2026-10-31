# Python

The portable rules are in
[../portable/rules/python.md](../portable/rules/python.md). This project adds
three:

- **No module docstring.** The file name says what the module is; a sentence
  beside it is a header. A docstring is for a signature a reader cannot decode
  on its own, and it stays on the function or the class it documents.
- **One class per file.** A file is one concept; two classes in it are two
  concepts, and the reader cannot tell which one the file is about.
- **Eighty lines of code at most, imports excluded; fifty is the target.** A
  file that grows past that holds several things: split it. Blank lines and
  comments do not count, imports do not count, everything else does.
- **An is-a hierarchy is an ABC, not a Protocol.** `Occlusion` is the contract
  and `HardOcclusion` / `SoftOcclusion` its implementations: `occlusion/base.py`
  is an `ABC`, each implementation a subclass in its own file. A `Protocol` is
  for a structural seam with an object the project does not own, and needs a
  reason.

[no-module-docstring.sh](../checks/no-module-docstring.sh),
[one-class.sh](../checks/one-class.sh) and
[file-length.sh](../checks/file-length.sh) check them.
