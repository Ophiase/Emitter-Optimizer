# Project guards

What one project allows another to reuse. A file-based convention, not a
policy engine.

## Files

- `.agents/guard.yaml`: this project's restrictions, versioned.
- `.agents/local/guard.yaml`: local overrides, never committed.
- Both are optional. A local value overrides the shared one.

## Format

```yaml
group: company-a
classification: confidential

reuse:
  code: allowed
  ideas: allowed
  attribution: allowed

publish: forbidden
```

The values are `allowed`, `forbidden`, or absent. Absent means relaxed.

## Reading another project

1. Identify the project.
2. Find its path in `.agents/local/projects.yaml`.
3. Read its `.agents/guard.yaml`, then `.agents/local/guard.yaml`.
4. Apply the last value for each key.

No guard is permissive. Projects of the same `group` may collaborate unless
a key says otherwise. Different groups do not imply restrictions. A missing
file is never confidential.

## The four permissions

| Key | What it covers |
| --- | --- |
| `code` | copying an implementation |
| `ideas` | reusing a concept or an approach |
| `attribution` | naming or linking the source |
| `publish` | making the content public |

They are independent: a project may allow an idea, forbid its code and ask
not to be named.
