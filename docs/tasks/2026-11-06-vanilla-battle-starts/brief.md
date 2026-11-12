# Brief: how vanilla starts a battle, and the standard we should build

**Study only. Read-only. Do not write a ROM, do not build, do not run the suite, do not edit a patch module.**
The owner stopped the arena work to get this answer first. Follow `docs\tasks\global.md`.

## Why

Our arena fight start has a hard camera jump. The owner played vanilla Piccolo against Android 17 and the
camera pans onto the player smoothly. His instruction: "check what else vanilla does for battles so we can see
how we are handling it. If anything can be built into our tooling so all future battles dont need this trouble
again, just a standard battle start."

So the deliverable is not an arena fix. It is the vanilla battle-start shape, written down, plus a proposal for
one reusable helper.

## What we already know, so do not re-derive it

Our record F, decoded from the shipped ROM `builds\mockups\2026-11-06-arena-v4\log2_poc_r41_arena_v4.gba`,
ending table `rom:0x3B8140` word 23:

```
leader(who=3) ; load_map_at(zone=6, area=100, var=1, x=248, y=568) ; face(set=0, dir=1)
header_bit1(value=1) ; bar_show(set=28)      next 26 = END
```

Bible row 930 says the vanilla relay Cell Jr fights end `push 1 ; ext 86 ; push 31 ; ext 85 ; push 0 ; ext 33`.
**So vanilla ends with `ext 33 (0)` and we do not.** That is the known diff. Confirm or refute it.

Measured from the owner's two states beside that ROM, `log2_poc_r41_arena_v4.ss2` (conversation) and `.ss3`
(fight), using Trunks' own 16x32 OAM box against his world spot (248,568):

| | live camera pointer `0x03000FF4` | camera read back |
|---|---|---|
| ss2 | `0x030020F4`, vtable `0x08025034` | (136, 456) |
| ss3 | `0x030020C0`, vtable `0x08025A6C`, the follow camera, actor `0x02030938` | (136, 513) |

x is identical, y moved 57 px. **Caution: that read assumes sprite dy 0.** Bible rows 217 and 846 record the
player at dy -24, and ss2's Trunks is an NPC set while ss3's is the party player, so dy may differ between the
two frames. Row 889 names a view struct reached through the ROM word at `0x083ED65C`, with x at +4 and y at
+8. Read that struct for values that need no sprite assumption, and say which method each number came from.

Bible rows to start from, already confirmed: 774 (ext 31 and ext 33, the follow ease of 3/64 x and 9/128 y),
775 and 776 (our own r30 hand-off, `ext 31 (648,296,255)` under black before `ext 33 (0)`, residual 2 px),
783 (a hand-back with no ext 31, 40 px eased over 78 frames), 930, 1038, 1048, 1169, 1978.

**Row 1048 and rows 774, 887 and 1038 conflict** on which object is the follow camera. 1048 calls
`0x030020F4` "a follow object"; the others put `ext 33`'s follow at `0x030020C0`. My measurement above agrees
with the latter. Open the handler and settle it. `whatis.py` finds `0x08025034` inside `sub_0802493C` at
+0x6F8 with one reference at `rom:0x23104`, and names it no further.

## The questions, in priority order

1. **Decode the tail of every vanilla battle start you can find.** Known tables: Android 19 `rom:0x3D40C8`,
   the self-destruct table `rom:0x3EB704`, Gohan's `rom:0x3EA400`, Vegeta's `rom:0x3EC758`, the relay hand-offs
   at `rom:0x3E9DFB` and `rom:0x3E9E5B`, and the vanilla ending record `rom:0x3B8016`. Find Piccolo against
   Android 17 as well; `--find-text "never tell you where he is"` returned nothing over
   `rom:0x3B0000-0x420000`, which is not proof it is absent, so widen the span or search another fragment.
   Report the shared shape and every deviation. Say how many battles you reached and by which search shapes,
   and name what a battle done a third way would look like.
2. **Does the engine's own control hand-back ease or snap?** Our record has no `ext 33`, yet ss3 is on the
   follow camera, so something installs it when the scene ends. Find that code and say whether it eases from
   the current view or replaces it. The owner's two states bracket the transition and cannot answer this, so
   answer it from the handler, not from the states.
3. **What does a vanilla battle start do about the player's form and sprite?** The owner reports Trunks loads
   as base, not Super Saiyan. ss2's Trunks is object `0x020351EC` and ss3's is `0x02030938`, a different
   object, so the conversation's NPC is replaced by the party player. Read `docs\tasks\2026-11-02-trunks-ssj\`
   and the `cellgames_ssj` and `fullpower_ssj` modules before proposing anything. Is there a vanilla op that
   sets a party member's form at battle start, or does vanilla never need one? Do not design a fix.
4. **Propose one reusable helper**, in words and a signature only, no implementation. Something a future
   battle calls to get the vanilla shape by construction: the op order, the camera hand-off, the HUD and bar,
   the form. Say where it belongs (`scene\scene_lib.py` or a new `scene\battle_start.py`), what it takes, and
   what it cannot know. Also say which existing tool should learn to CHECK a record for the shape, so a
   missing `ext 33` is caught before a build instead of in play.

## Rules

- Tools first: `docs\tool-index.md` lists them. `scene\scene_probe.py`, `scene\scene_lib.py`,
  `rom\whatis.py` and `rom\state_dump.py` already do most of this. Writing a second tool is the default
  failure here. Put any study script in `scripts\one-time\2026-11-06-vanilla-battle-starts\`.
- Label every claim CONFIRMED (address plus bytes or disassembly), LIKELY or SPECULATIVE. Quote the proving
  line. Read a handler from `GitHub\legacyofgoku2-disasm\build\code`, never the stale gnu tree, and look an
  address up in that repo's `docs\CODE_INDEX.md` rather than reading a missing file as a missing function.
- Say "the search returned nothing", never "it does not exist".
- Write `docs\tasks\2026-11-06-vanilla-battle-starts\report.md` and `rows.md`. `rows.md` holds only facts the
  bible does not already have, as `## Section N` table blocks, tag `VBS`.
- No em or en dashes in any file.

One report message, then stop. Do not add a byte order mark.
