# Sprite suite: design

A pipeline that turns a vanilla animation into a finished outfit swap, with the checks built in.

Status: design, agreed with the owner on 2026-11-05. Not built.

---

## 1. Why this exists

The outfit swap work does not scale. Every frame costs a round of the owner's eye, and the same
mistakes keep coming back. The down run cost two rejected drafts before the pose was even read.

The owner's words set the target. He hands me an animation. I hand back frames and a GIF. They need no
changes, or minimal ones. Not him complaining that I repeated mistakes, and not output that came out
terrible.

> **The suite does not help the owner review. It stops bad frames reaching him.**

The manual checks in this pipeline are MINE, not his. He stays the final judge, by eye, in mGBA. He
should never be the one who catches that I repeated myself.

### The cost model that shapes everything

The owner named the real constraint: reviewing every single frame by hand costs a lot of time AND a lot
of tokens. So the eye is the expensive resource, his and mine.

**The eye gets spent once, on the gold master. After that, the per-frame cost must be a check, not a
look.** A frame only earns eye-time when a check fires, or when the pose genuinely changes what the
garment does. That is how one direction grows into a whole set without the cost growing with it.

---

## 2. The two failures this must prevent

The owner named both. Every check in the suite traces to one of them.

### Failure A: the pose

The returned frames do not match the intended frames. The limbs do not agree with each other across the
row, or with what the vanilla frame was actually doing.

His example: the first down run draft. "The arm that is in front of him is mostly gone in yours, and the
whole other side is just wrong. It should be his other arm behind him."

### Failure B: the outfit against the gold master

The garment does not express correctly in that frame's view and pose.

His two examples, and they are the same error:

| Case | What I drew | What was true |
|---|---|---|
| Trunks tank | no exposed chest | the vanilla frame showed it and the reference showed it |
| Gohan gi | the sash as a straight line | he stands diagonally and the rest of his clothes run diagonally |

That is not a drawing slip. It is treating a garment feature as a flat rule instead of asking what that
feature does in THIS frame.

> **The garment is not a set of pixels to copy. It is a list of named features. Every frame owes an
> answer for every feature: shown, hidden by the pose, or turned to match the view.**

The owner's summary of both failures together: "if nothing matches or it looks like a mess, where
nothing looks intentional".

---

## 3. What the owner decided

Recorded as he decided it. These are not open.

| Decision | His call |
|---|---|
| **References are a prerequisite** | He provides them into a references folder per outfit, as he did for the Trunks tank. Includes reference sprites made to order at the angles the game uses, which beat low quality anime screenshots. **No references, no gold master work.** The suite says so rather than guessing from the vanilla. |
| **The gold master** | The idle front, back and side frames. Decided by us together, against the references. Everything after that must match it. |
| **Unit of work** | Start at one direction of one animation. Then all directions of one animation. End goal is all animations in one shot. |
| **Gate behaviour** | Fix minor problems, carry on, show the list at the end. Stop and ask only for something major: a missing limb, or something very odd that I cannot conclude myself. A stray pixel is minor. |
| **First job** | Lock the Trunks tank gold master. It was approved piecemeal and there is no agreed front, back and side set for the rest to match. |
| **Enforcement** | A skill the harness makes me load every time. Not a document I am merely told to read. |
| **Scope** | Outfit swaps onto existing vanilla frames. The vanilla frame supplies the pose and the silhouette. |
| **Handback** | Frames, a GIF, and a short list of what I fixed on my own call and what I am unsure of. No wall of text. |

### Why a skill and not a document

The owner picked this deliberately. `docs\sprite-guide.md` already held the pose method, including the
exact steps I skipped on the down run. Having it written down did not make me open it. A skill the
harness loads removes the choice, and skipping a step becomes a visible violation rather than a quiet
shortcut.

---

## 3b. Decisions from the builder check

A fresh reviewer read this document and raised five questions. The owner answered four on 2026-11-05.

| Question | His call |
|---|---|
| **Does the gold master apply backwards?** The manifest already holds 32 approved tank PNGs. | **Check them, show the list, change nothing.** The finished suite runs over all 32 as a READ ONLY pass and hands him a list of anything that disagrees. He decides per frame. No shipped art moves on the suite's word. This also tests the checks against art whose answer is already known. |
| **What happens to the Super Saiyan twin?** Set 134 is never drawn: every frame is the base body plus the Super Saiyan head, derived by rule. | **Same pass. Derive and check both.** They share one body, so running them apart is how the two drift, and this proves the one body rule every time. The sprite guide's rule stands: state what the derivation drops, do not ask. |
| **Does a pass end at a ROM?** | **No. Builds go on an approved queue.** Finished art accumulates. Two builds are approved as part of the workflow and need no further permission: **one when the initial walking animation is done, and one when all animations are done.** Any build between those two is his call, asked for at the time. His reason: a build costs time and money, and the per pass cost is what the suite exists to cut. |
| **What is the per frame eye budget?** Naming body parts cannot be automated, and the down run cost four hand lettered maps. | **Letter the gold master once, project it onto the rest.** The suite carries the gold master's naming onto each new frame and flags only where the projection does not fit. Hand lettering is spent only on flagged frames, so the cost grows with how unusual a pose is and not with how many frames there are. |

The fifth question, what event loads the skill and whether it binds the drawing agents, is the builder's
to settle, with one constraint: **a harness hook is a change to `settings.json` and needs the owner's
explicit approval before it is built.** Until then the skill is invoked by name at the start of any
sprite work, and its contract is restated in the brief of every agent that draws.

> [!IMPORTANT]
> The projection in the last row is the least explored idea in this design and the one most likely to
> need a rethink. It is what makes "all animations in one shot" affordable, and nothing has been built
> that does it. Plan it first and prove it on the down run, whose answer is already known.

## 4. Goals

1. One pass over a `(set, anim, dir)` returns frames, a GIF and a short report.
2. Every check exists because of a named past failure. No check is added on theory.
3. Checks are machine decidable wherever a machine can decide. The eye is reserved for what only the eye
   can do.
4. The suite grows. Adding a check when something slips through is routine, not a rebuild.
5. The pass works unattended, start to finish, and only stops for the major cases above.

## 5. Non-goals

- Drawing new poses from scratch, where no vanilla frame supplies the pose. Deferred, with a clear place
  left to add it.
- Anything the owner runs himself. He never drives this.
- Replacing the owner's eye as final judge.
- Naming body regions automatically from colour. Already proven impossible, see section 7.

## 6. Anti-goals

These mean the suite failed even if every check passed.

- **Output that passes the checks and still looks like a mess.** The checks are a floor, never a
  substitute for the frame reading as drawn.
- **Pixels that look plausible but not intentional.** A rule pass that produces a defensible average is
  the exact failure the owner rejected twice on the down run.
- **A pass that costs more than doing the frame by hand.** If the ceremony outgrows the work, it is
  wrong.

---

## 7. The hard constraint the builder must not fight

From `docs\sprite-guide.md`, and it is settled by experiment, not opinion.

Four automatic body finders were tried on the Trunks side walk and all four failed: a high nibble palette
ramp, a hue cluster, a skin plus ground filter over the medial axis branch ends, and motion across the
cycle. They failed for one reason. **The artist reuses palette ramps, so no index, hue or ramp names a
part.** The eye white is also a hair highlight. The iris blue is also the jacket. The belt orange is also
the scabbard. A filter over colour cannot separate what the colour does not separate.

So naming regions stays hand work. The suite's job is to make that hand work cheap, to prove the
transcription, and to make a wrong call visible. It must never try to replace it.

This session re-proved the same point three times on the down run. The wide black blob at the feet is
boots, not a shadow. The brown flanking the face is the face, shaded dark at its edges. The grey at the
upper left is the sword hilt. No colour rule would have got any of the three right.

---

## 8. What already exists

The suite is assembled from these, not written fresh. All are in `scripts\permanent\`.

| Tool | What it gives the pipeline |
|---|---|
| `rom\log2_sprites.py` | export a set to indexed PNGs |
| `rom_sheet.py` | locate the frames of one `(set, anim, dir)` |
| `rom\sprite_look.py` | render any frames big, with the palette index in every cell |
| `rom\show_regions.py` | draw a hand written region map back over its frames, prove the transcription, draw the joints |
| `rom\sprite_loop.py` | build a looping GIF and a labelled strip from any frames |
| `rom\sprite_guard.py` | hold an outfit swap to the garment, and show what changed |
| `rom\sprite_stats.py` | measure the pose signature of an animation row, and name the frame that breaks it |
| `docs\sprite-guide.md` | the method, and the lessons behind every rule in it |

`show_regions.py` was promoted out of a one-time folder in this session, made to read its frame list from
the regions file so it runs on any set, and given a joints panel.

### Facts the builder will trip on

- **ROM frame bytes are TILE order. The PNGs in `art\` are ROW order.** `image_to_tiles()` converts. For
  a 16 wide frame the head and body split lands on the same byte in both orders. That coincidence does
  NOT hold at 32 wide.
- **Frame sizes are 16x32 (512 bytes, dx 0) or 32x32 (1024 bytes, dx -8).** Mixed rows exist: anim 13
  run, anim 12 flight and anim 5 ki blast are 16 wide for dirs 0 and 1 and 32 wide for dirs 2 and 3. The
  whole swap path today assumes 16 wide. **The side directions need this before they can run.**
- A set's own embedded palette is often not the one the game draws it with.
- Art rules from `CLAUDE.md` bind the suite: Buu's Fury art may be ported, other modders' art never, and
  the Z Hack is clean-room inspiration only.

---

## 9. Known gaps, which is most of the build

| Gap | Why it matters |
|---|---|
| No single step from `(set, anim, dir)` to frame PNGs | every job starts with hand assembled header addresses |
| 32 wide frames unsupported in the swap path | blocks every side direction, which is half the work |
| No gold master concept anywhere in the tools | the thing every frame must match does not exist as an artefact |
| No garment feature ledger | failure B has no mechanism behind it at all |
| No cross frame consistency check | failure A has no mechanism behind it at all |
| The handback is assembled by hand each time | the report the owner reads is improvised |

---

## 10. What is left to the builder

Deliberately open. The owner decided the shape, not the mechanism.

1. **The step list, and which steps are gates.** Section 3 fixes the gate behaviour, not where the gates
   sit.
2. **The gold master artefact.** What a gold master is on disk, what it carries beyond three PNGs, and
   how a later frame is measured against it.
3. **The garment feature ledger.** How a feature is named, and how a frame records its answer of shown,
   hidden or turned. This is the heart of failure B and the least explored part of the design.
4. **The check list and its thresholds.** Each one must name the failure it came from.
5. **Where checks live**, in the tools or in the skill, and how a check reports minor against major so
   the gate behaviour in section 3 works.
6. **The skill's structure**, and how it forces the pose read that got skipped.
7. **The report format** for the handback in section 3.

### A suggested first slice, for the plan to argue with

Smallest thing that proves the design: the Trunks tank gold master, then the down run as the first
animation through the full pipeline. The down run already has its references, its region maps, its
joints and its pose reading from this session, so the pipeline can be measured against work whose answer
is known.
