# Python

The portable rules are in
[../portable/rules/python.md](../portable/rules/python.md). This project adds
one:

- **No module docstring.** The file name says what the module is; a sentence
  beside it is a header. A docstring is for a signature a reader cannot decode
  on its own, and it stays on the function or the class it documents.

[no-module-docstring.sh](../checks/no-module-docstring.sh) checks it.
