# Brief: the implementation plan for the sprite automation suite

## What this is

The owner approved a design. The next artefact is the PLAN, not code. **Write no production code and
build no ROM.** Reading, measuring and small throwaway probes under
`scripts\one-time\2026-11-05-sprite-suite-plan\` are fine and encouraged, because a plan that guesses at
what the existing tools return is worthless.

## First action

Invoke the skill `superpowers:writing-plans` with the Skill tool and follow it in full. It owns the plan
format: the header block, Global Constraints, Review Focus, the Files and Interfaces blocks per task, the
step granularity, and the self-review at the end. Do not work from memory of it.

One deviation from that skill, and it is the owner's standing preference: **plans live in
`docs\design\plans\`**, not `docs\superpowers\plans\`. Name the file
`2026-11-05-sprite-suite-plan.md`.

## Read these four, in this order

| File | Why |
|---|---|
| `docs\design\2026-11-05-sprite-suite-design.md` | the spec. 228 lines. Section 10 is what is left to you |
| `docs\sprite-guide.md` | the method the suite automates. 1098 lines. Read it ALL before you plan a check |
| `docs\tool-index.md` | what already exists. The suite is ASSEMBLED from these, not written fresh |
| `docs\design\plans\2026-10-16-slice1-poc-plan.md` | the house plan format, for tone and shape |

Then read the actual source of the tools in design section 8 that your plan calls. Their docstrings are in
the tool index; their real signatures and return values are not.

## What the plan must settle

Design section 10 lists seven open items. All seven are yours. The design also flags the one most likely
to need a rethink, and it is the one that makes the whole thing affordable:

> The gold master's region naming is PROJECTED onto each new frame, and only the frames where the
> projection does not fit get hand lettered.

**Plan that first and prove it on the down run**, whose answer is already known and already written down
in `docs\tasks\2026-11-05-trunks-run\pose.md` and `regions.txt`. If you measure it and the projection
cannot work, say so plainly and plan what replaces it. A design flag is an invitation to find the
problem, not an instruction to agree.

## Constraints the plan must carry into every task

- The hard constraint in design section 7: **no colour rule can name a body part.** Four automatic body
  finders were tried and all four failed. A plan task that tries a fifth is a rejected task.
- `docs\tasks\global.md` applies in full. Absolute paths only, never `cd`, `Set-Location` or
  `Push-Location`. Python is `py -3.14 -P`.
- Never write under `data\`. Never overwrite a ROM, save or state.
- No em dash, no en dash, anywhere. No byte order mark.
- A harness hook is a change to `settings.json` and needs the owner's explicit approval before it is
  built. The design's fifth builder question is yours to settle under that constraint.
- Two builds are pre-approved by the owner and need no further permission: one when the initial walking
  animation is done, one when all animations are done. Any other build is his call at the time. Your
  plan's tasks must respect that; a task that ends in an unapproved ROM is a wrong task boundary.
- Art rules from `CLAUDE.md` bind the suite: Buu's Fury art may be ported, other modders' art never, and
  the Z Hack is clean-room inspiration only.

## Scope check, which the skill asks for and which matters here

The design may be more than one plan. If the gold master artefact, the garment feature ledger and the
32-wide frame support are independent enough to ship separately, say so and plan the FIRST one properly
rather than all three thinly. Name the others and what they would need. The owner would rather have one
plan he can execute than three he cannot.

## If the harness refuses your file write

Two agents today were refused a report file write with "Subagents should return findings as text". Code
writes were allowed; document writes were not. If that happens, **return the complete plan text in your
report message** and the controller will save it. Do not shorten it, and do not silently drop it.

## Report

State: which of the seven open items you settled and how, what you measured rather than assumed (with the
command and its output), the one thing in the design you think is wrong or unaffordable, and anything
only the owner can decide. Flag every claim CONFIRMED, LIKELY or SPECULATIVE.

One report message, then stop. Do not add a byte order mark.
