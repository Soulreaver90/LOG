# Z Hack source files: moved to `zhack\sources\`

The two files that were here are another modder's work. They now live in `zhack\sources\`.

| File | SHA-1 | Bytes | Now at |
|---|---|---|---|
| `zhack_patched_eu.gba` | `b9646491a947fb3f3a63c814f39e2d465698335d` | 9,239,056 | `zhack\sources\zhack_patched_eu.gba` |
| `zhack_beta.ips` | `f70fcb66baa17fcb0a457a77b95ada4dba5598de` | 1,016,873 | `zhack\sources\zhack_beta.ips` |

Both files are byte identical to the copies that were here. Nothing was deleted.

## Why they moved

The project rules keep `zhack\` out of the git repository, because the Z Hack is clean-room inspiration only. These
two files sat outside `zhack\`, inside `docs\`, so that rule did not reach them. A public repository must never
carry another modder's ROM or patch. The move puts them under the folder the rule already names, and the root
`.gitignore` excludes `zhack\`, every `*.gba` and every `*.ips` as well.

> [!NOTE]
> Older briefs, reports and ledger entries still name the old path. They record history and keep their wording.
> This page is the signpost for a reader who follows one of them here.

## What the rule still is

The project rules say it plainly. The Z Hack is studied into written rules only. No art, no module and no
build takes anything from `zhack\`.
