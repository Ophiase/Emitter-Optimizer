# Hardcoded URLs

A URL written in code is an address someone will have to find and change by
hand — in a test, in a demo, in a default. It is the exception here, the way
a comment is, and it has to be justified the same way.

[hardcoded-url.sh](../checks/hardcoded-url.sh) reports every `://` and every
`scheme="..."` on the `.py` and `.js` lines the working tree added.
Fixtures are data, not code, and are skipped: the project lists their folders
in `hardcoded-url.ignore`.

## Take it out first

- **A service address** comes from the typed config, with no default: the
  environment that runs the service knows where its neighbours are, the code
  does not.
- **A test against a fake server** lets the fake own the transport
  (`httpx.MockTransport`, `ASGITransport`) and its address, so the test
  itself never spells one.
- **A value under test** — a redirect target, a callback — is built from what
  the test already holds, or comes from a fixture.

Hiding the URL does not remove it. `f"{scheme}://host"`,
`httpx.URL(scheme=..., host=...)` and a string split in two are the same
address, and the detector looks for the first two on purpose.

## When it has to stay

Some do: a public provider endpoint, the external format a regex matches, the
address a library insists on before it lets a mock answer. Keep it with a
directive on the line itself or on the comment line right above:

```python
# hardcoded-url: httpx needs an absolute URL, the mock never dials it
ADDRESS: Final = httpx.URL(scheme="https", host="docling.invalid")
```

The reason is three words at least, and you say in the turn which URL you
kept and why. The developer decides — having to write the reason is usually
what finds the way to do without.
