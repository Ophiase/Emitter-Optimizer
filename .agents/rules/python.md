# Python

The portable rules are in
[../portable/rules/python.md](../portable/rules/python.md). This project adds
three:

- **No module docstring.** The file name says what the module is; a sentence
  beside it is a header. A docstring is for a signature a reader cannot decode
  on its own, and it stays on the function or the class it documents.
- **One class per module, grouped in a package.** A class is a concept; a
  settings/result pair is one concept and becomes a package with one module per
  class, not a file holding four.
- **Short by default; 200 lines of code is the ceiling.** Past 80 lines a
  check flags the file as a question, not a fault; past 200 it fails. Imports,
  blank lines and comments do not count. A long file is rare, and it is a
  decision, not a habit.
- **An abstraction owns its operations.** A class that acts on something owns
  the methods that act on it, exposed by autocomplete: `Segments.visibility`,
  `Absorption.from_segments`, `Scene.of`. No module of free helpers that a
  reader has to discover by grep.
- **A callable role is a Protocol with `__call__`, not a `Callable` alias.**
  `Callable` names a shape, not a responsibility; the `callable-alias` check
  prints every one so it can be named. A callback protocol may declare only
  `__call__`; an is-a hierarchy is still an ABC, not a Protocol.
- **An is-a hierarchy is an ABC, not a Protocol.** `Occlusion` is the contract
  and `HardOcclusion` / `SoftOcclusion` its implementations: `occlusion/base.py`
  is an `ABC`, each implementation a subclass in its own file. A `Protocol` is
  for a structural seam with an object the project does not own, and needs a
  reason.

[no-module-docstring.sh](../checks/no-module-docstring.sh),
[one-class.sh](../checks/one-class.sh) and
[file-length.sh](../checks/file-length.sh) check them.
