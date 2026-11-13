# Structure review, 2026-11-13 (Grok 4.7 high, verified)

Raw output: `scratch\cursor\2026-11-13-structure\out.md`. Nothing below is relayed raw. Each item
says whether I checked it against the real files.

## Decisions this changes

### Move B is CANCELLED: do not merge `docs\tasks\` with `scripts\one-time\`

**CONFIRMED.** `.gitignore` ignores all of `scripts\one-time\`; `docs\tasks\` is tracked. Merging
puts tracked and ignored content in one tree, so `git add` on a task folder would sweep up probe
dumps, and `git clean -fdx` would delete the only copy of a one-time script.

Replacement: keep the git boundary, keep the matching folder names on both sides, and add a test
that every `scripts\one-time\<name>` has a `docs\tasks\<name>` twin. A pointer, not a merge.

This was the owner's "merge" instruction. It needs re-approval before anything else happens to it.

### Move A stays, with two blockers named

**CONFIRMED.** Two tests read the directory directly and would NOT follow a change to
`log_paths.BUILD_LISTS`:

    scripts\permanent\tests\test_trunks_tank.py:26        LISTS = log_paths.PERMANENT
    scripts\permanent\tests\test_vegeta_ssj_scene.py:33   LISTS = log_paths.PERMANENT

Also: `log2_build._expand_list` resolves `include` as `path.parent / name`, so all 24 lists must
move together or an include raises. That part fails loudly. The quiet part is that nothing asserts
the glob count, so a list left behind just disappears from `docs\status.md`.

Plan: move all 24, set `BUILD_LISTS = PERMANENT / "build-lists"`, repoint those two assignments,
update the command lines in `README.md` and `CLAUDE.md`, and assert both that the new folder holds
24 and that `PERMANENT` holds zero.

### Move C is mostly done already

**CONFIRMED.** `scripts\permanent\` already has `art`, `disasm`, `emu`, `map-editor`, `rom`,
`scene`, `patches`, `tests`, `docs`. Only the 24 lists are loose. Moving `patches\` or `tests\`
would break `import patches` and the documented `unittest discover` command. Do move A, stop there.

## Rot found, all CONFIRMED

1. **`docs\tool-index.md` is stale.** Line 209 still lists `art\golden\work`, a path the art move
   retired. `test_make_tool_index.py` checks `build()` in memory and never reads the file on disk,
   so the suite cannot see it. Same class as the status page.
2. **Nothing runs `make_status.py` in the suite.** A forgotten regeneration leaves the health
   section reporting `none` from the previous run.
3. **`build_file()` does not search `builds\mockups\`.** `test_scene_probe.py`'s arena class skips
   on its own path, outside the helper that fixed the other skips.
4. **Skips still hide missing files.** `unittest` exit 0 includes skips. Eight test files skip when
   a historical ROM, save or state is absent. The folder hole is closed by
   `test_log_paths_exist.py`; the FILE hole is the same shape and still open.
5. **`.gitignore` un-ignores art build inputs one folder at a time.** A new build-input folder under
   `gohan\` would be absent from a clone with no test noticing, because the files are present here.

## Art split: half done, CONFIRMED

- `art\effects\_buus-fury-reference\` is reference art inside the approved-art folder, while other
  rips live in `art\reference\vanilla-sets\`. Two homes for the same kind of thing.
- Auras are in three places: `characters\cell\aura`, `characters\gohan\gi_*_aura`,
  `effects\_buus-fury-reference\aura`.
- Portraits are in three places: `art\portraits`, `art\portraits\sources`, `art\tables\portraits`.
- `art\README.md` still describes the pre-move flat tree, and its "Not moved yet" table lists
  destinations equal to the sources.
- `art\tables\README.md` still tells the reader to pass `art\portrait-sources\remaster\...`.
- `art\palettes\` is a real subject with no registry constant, so the literal guard cannot see it.

## Guard blind spots, CONFIRMED and now written down

`test_no_folder_literals.py` cannot see: non-`.py` files (`.js`, `.mjs`, `.lua`, the build lists,
every README); a folder the registry does not name (`art\palettes`); a full path handed to `open`,
`Image.open` or `glob`; a name built by concatenation, `.format`, `%` or `join`; case differences
(the set is case-sensitive, Windows is not); bytes literals; and docstrings, so
`test_gi.py` lines 6-7 can keep describing `art\gi_base` while the code is right.

## Status-page drift the health check cannot report, CONFIRMED

- Item MARKS are never read. `LKT-2` is IN while `gohan_gi` ships in dev only.
- A code may name the WRONG module and pass, as long as that file exists.
- A Reference row with a third column or backticks does not match the regex and vanishes silently.
- The Test column looks for `test_<module>.py`, so eight modules read as untested when they are
  tested under another name, among them `gohan_gi` (in `test_gi.py`) and `ssj2_form` (`test_ssj2.py`).

## Not acted on yet

Every "smallest fix" above is logged in `docs\backlog\active-todos.md`. The two blockers for move A
and the cancellation of move B are the only items that change what happens next.
