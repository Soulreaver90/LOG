# Repo prep: group the tools, and make the folder safe to push (me, 2026-10-31 morning: "Go ahead with the cleanup/reorg")

Read `README.md` (the "where does X go" table),
the project rules (the git section names what must never go in the repo), and `scripts\permanent\log_paths.py`.
A backup of the whole of `scripts\permanent` is already at `archive\backups\2026-10-31_pre-tool-reorg\permanent`.

## Part 1: group the permanent tools by purpose

`scripts\permanent\` holds 28 flat `.py` files. The workspace standard asks for `permanent\<purpose>\`. Only `emu\`
follows it today. Proposed grouping, which you may adjust with a stated reason:

| Folder | Tools |
|---|---|
| `rom\` | `log2_build.py`, `log2_save.py`, `log2_sprites.py`, `rom_info.py`, `rom_sheet.py`, `rom_space.py`, `find_compressed.py`, `find_palettes.py`, `webfoot_decompress.py`, `webfoot_lz_pack.py`, `thumb_dis.py`, `re_sym.py`, `state_dump.py` |
| `art\` | `gi_art.py`, `gi_aura.py`, `gi_one_body.py`, `gi_post.py`, `gi_review.py`, `hand_frames.py`, `inject.py`, `art_tables.py`, `beam_struggle_art.py`, `frame_lock.py` |
| `scene\` | `scene_lib.py`, `scene_probe.py`, `scene_harness.py`, `map_view.py` |
| stays put | `emu\`, `patches\`, `tests\`, `disasm\`, `ghidra\`, `review\`, every `build_list*.txt`, and `log_paths.py` |

**`log_paths.py` stays at the root of `permanent\` and every build list stays where it is.** Build list paths appear
in dozens of commands, briefs and docs; moving them would break all of them for no gain.

Update every import, every CLI path inside our own scripts, and every path in `docs\playbooks\*` and
`docs\tasks\2026-10-30-tooling\*` that names a moved tool. Do not rewrite old task reports: they describe history.
Prefer a package import (`from rom import log2_build`) or whatever the existing style uses; match the surrounding
code rather than inventing a new convention.

## Part 2: the file that must not be in a public repo

`docs\research\sources\zhack-2026-10-30\zhack_patched_eu.gba` is another modder's ROM, sitting inside `docs\`.
the project rules bars `zhack\` from the repo but this copy is outside that folder. **Move it** (never delete it) into
`zhack\sources\` keeping its name, and leave a short `README.md` where it was saying where it went and why. Check for
any other ROM, save or state under `docs\` and move those the same way.

## Part 3: `.gitignore`

Write `.gitignore` at the root. It must exclude, with a comment per block saying why:

- `builds/`, `data/`, `zhack/`, `archive/`, `scratch/` (the last two are 3.3 GB and 1.3 GB and hold 446 ROM, save
  and state files; the project rules names only the first three, so say in the file that the rule is wider than that line)
- every `*.gba`, `*.sav`, `*.ss[0-9]`, `*.ips` anywhere, as a belt-and-braces rule
- `scripts/one-time/` (205 MB of probe output, ROM copies and a Ghidra log)
- `test-data/` (holds `.sav` files)
- `__pycache__/`, `*.pyc`, `.pytest_cache/`, `LOG.code-workspace`

Then **prove it**: with `git init` in a scratch copy or with `git check-ignore`, produce the list of files that WOULD
be committed, and its total size. Report the count and the megabytes. It should be well under 200 MB and must contain
no `.gba`, `.sav` or `.ss*`. **Do not run `git init` in the real LOG folder and do not create any commit:** I
signs in and makes the first push himself.

## The gate, absolute

- **Every one of the ten `build_list*.txt` rebuilds byte-identical.** Main `build_list.txt` to `14d6b831`. Trials:
  Cell Jr `db015ae8`, chapters `1bb86930`, gi base `d012a9f4`, Vegeta 19 `0598a127`, sprite lab `fea0aeb0`, and the
  four alias lists to main. Build to a scratch path with `--out` and `--log`; never overwrite a ROM.
- **The full suite passes.** It was 1087 tests before you started.
- If a move would break something you cannot fix cleanly, leave that tool where it is and say so in the report.

## Report

Short. `docs\tasks\2026-10-31-repo-prep\repo-prep-report.md`: SHIPPED and PENDING tables, the before and after tool
layout, every file moved, the rebuild proof as (list, expected, built), the suite count, and the would-be-committed
file count and size. Label claims C, L or S.

## Limits

- Python: `py -3.14 -P`. Never write under `data\`. Never overwrite or delete a ROM, save or state: moves only.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. Six tasks in a row have broken this rule. Do not be the seventh.
- Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `builds\`, `archive\` or the contents of `zhack\` other than
  adding the moved file. Do not create a git repository or a commit.

