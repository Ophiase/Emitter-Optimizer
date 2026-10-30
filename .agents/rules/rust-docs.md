# Rust documentation

A `///` is read in an editor's hover, next to the signature. It earns its
place by saying what the signature cannot: a unit, a frame or an order
convention, an edge case, the reason a default is what it is.

- **Never a paraphrase of the name.** `/// The points.` above `fn points`,
  `/// How many.` above `count`: delete them.
- **No lint forces a doc.** `missing_docs` stays off: it turns every field
  into a paraphrase.
- **`# Errors`** says which input fails and why, not the list of variants.
- **A type's doc** says what its values guarantee (non-empty, finite, a
  proper rotation), which is why the type exists.

[doc-slop.sh](../checks/doc-slop.sh) reports the one-line docs that only
repeat the name, or are two words long without a unit or code in them.
