# ShadowLock link file

Author: Aziel Eliab.

4DMap reads ShadowLock’s local link record so a person can see linked Softwares and their inputs in time order. ShadowLock’s repository does not publish this file yet. Both programs use this path and shape.

## Path

1. `4dmap shadow --links PATH` when a path is given.
2. Otherwise the `SHADOWLOCK_LINKS` environment variable.
3. Otherwise `~/.shadowlock/links.json`.

A missing file means there are no links. 4DMap does not create the file.

## Shape

Format name: `shadowlock-links-1`.

```json
{
  "format": "shadowlock-links-1",
  "links": [
    {
      "slug": "azmail",
      "input_id": "inbox/sample",
      "input_path": "samples/inbox.json",
      "linked_at": "2026-09-24T14:00:00Z",
      "label": "Morning intake",
      "kind": "plain"
    }
  ]
}
```

A bare JSON array of those objects is also accepted.

| Field | Required | Meaning |
|---|---|---|
| `slug` | yes | Softwares product slug |
| `input_id` | one of the two inputs | Input id or handle |
| `input_path` | one of the two inputs | Input path |
| `linked_at` | no | When the link was written, ISO-8601 |
| `label` | no | Business label |
| `kind` | no | Softwares kind as written, such as `plain`, `gate`, or `lock` |

A record with no slug, or with neither input field, is skipped. 4DMap shows the fields that are present. It does not invent a kind, a time, or a label.

`4dmap shadow` prints a short list. `4dmap shadow --json` prints the machine object (`op` is `shadow_links`). The local workbench reads the same file at `GET /v1/shadow_links`.

Sample file: [`examples/shadowlock-links.json`](../examples/shadowlock-links.json). It is not loaded unless you point `--links` or `SHADOWLOCK_LINKS` at it.
