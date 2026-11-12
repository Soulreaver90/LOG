# Retrospective: the Trunks tank side row

What the three generations of this row show about how I fail. Written 2026-11-01, after the owner asked why
the same mistakes keep coming back.

Compare for yourself: `scripts\one-time\2026-11-01-trunks-side-walk\three_versions.png`.

---

## 1. What the picture shows

| | What it looks like |
|---|---|
| **Vanilla** | The jacket is a crisp dark mass. It DEFINES the torso edge and separates both arms from the body. |
| **My first pass** | Bloated and mushy. The torso is one wide tan mass and the arms dissolve into it. |
| **Final** | Slimmer. Every limb carries a dark edge against the body. |

The single sentence that explains my first pass: **I removed the jacket and did not replace the job it was
doing.** The jacket was not only clothing, it was the separation between limb and torso, and the outline of
the silhouette. Take it away and paint skin in its place, and the character loses his edges.

Every one of my arm failures is a variant of this: thick arms, an amputated arm, a phantom arm at x8-9, an arm
sprouting from the hip. None of them were colour mistakes. All of them were **anatomy** mistakes.

---

## 2. The six blind spots

### 2.1 I model a sprite as indexed pixels. He models it as a body.

Every rule I wrote had the form "if the vanilla pixel at P holds index X, paint Y". That is a lookup table.
Not one of my rules ever encoded *this is an upper arm, about 3 px wide, it hangs from a shoulder and ends in
a hand*. He draws from anatomy. I substitute indices. That is why all four arm defects were anatomical, and
why no amount of palette care would have prevented them.

### 2.2 Every proxy I built could be satisfied by damage

This is the core engineering failure and it recurred about five times.

| Check | Damage that SATISFIES it |
|---|---|
| "the silhouette must shrink" | deleting his eye |
| "skin count in range" | a filled sleeve raises it, a lost arm lowers it, both land plausible |
| "no jacket index left" | painting the jacket indices anywhere, including the iris |
| "the lit column holds" | skipping the rows that have no highlight |

**Rule from this:** before trusting a check, write down what damage would satisfy it. If the answer is not
"nothing", it is a pointer, not a gate.

### 2.3 My review is scoped to my own intent

I only look where I worked. The eye sat outside my intent, so it was invisible, even though it was in review
sheets I opened several times at 22x. My invariant that pass was literally "nothing changed outside rows
16-25", which a broken eye on row 13 passes cleanly, because I did not break it on that pass.

**I verify my diff. I do not verify the character.**

### 2.4 I generalize from the sample in front of me without asking what it cannot contain

- Measured his arm against the **sleeve**, because the sleeve was what I had. His arm is 3 px, the sleeve 6 to 8.
- Measured arm highlighting against **hand** statistics. Vanilla Trunks owns no bare upper arm, so that sample
  could not answer the question at all. It nearly made me strip the arm.
- Measured the lit column in **absolute x**, which calls every diagonal arm broken.

Each time the number was real and the reference was wrong, which is worse than having no number, because a
wrong number looks like evidence.

### 2.5 I state conclusions above the confidence of my evidence

"The back idle confirms these rules" (it contradicts them, same defect at y19). "Never use 15" (the approved
front idle uses it 7 times). "[holds]" (the check was skipping the failing rows).

### 2.6 I fix the artifact, not the source

Three copies of one drawing diverged: side stand 1, front stand 1, the Super Saiyan side. The front one had
been stale for several rounds. Then the provenance script called the CORRECT frames stale, because it did not
know about the later hand edits.

---

## 3. The eye, as the clearest single case

`4F` and `51` are the jacket. They are also the iris and its shadow, two rows higher. A mask told to repaint
every `4F` and `51` repainted his eye: the bright half went dark, the lower half was cut to transparent. He
shipped with a dark smear for a face.

Three separate defences all failed:

1. `--body-from 13` does not protect it, because **the eye IS on rows 13 and 14**.
2. The silhouette check **rewarded** it.
3. My visual review never rendered the head, because I was working on arms.

The fix is not a row number per character. The garment is a **connected mass**; palette reuse on the head is a
small isolated island. Over 12 vanilla Trunks frames, every real garment component holds 27 px or more, and
every eye is an isolated 2 px component above the garment's top row. Separate by connectivity, protect the
islands, and name what was protected.

---

## 4. What I change

1. **Look first, unguided, at the WHOLE figure, before running anything.** A look that follows a measurement
   only confirms the measurement.
2. **For every check, write what damage would satisfy it.** Then say gate or pointer.
3. **Before generalising from a sample, write what the sample cannot contain.**
4. **State the anatomy before touching pixels.** Per limb: where the shoulder is, how wide, where the hand is,
   which edge faces the light. If I cannot say it, I cannot draw it.
5. **One drawing, one source.** If a drawing exists in N files, N-1 are generated and must be regenerated.
6. **Label every claim measured, assumed, or inferred from one sample.**

---

## 5. The honest limit, and its opposite

Across this row my unaided hit rate on arms was zero. He corrected every one. The scripts are worth keeping,
because they caught the amputated arm and scored a bad rule at 46% before he saw it. But they are a net under
the work, never the work. **He holds the intent. My job is to build him the view, not the verdict.**

**And "he holds the intent" is not "he is always right".** His own words: his version is subjective and may
not be perfect. The final is much closer to the intent than mine, which is the thing that matters, but it is
not a reference frame to be copied without judgement.

Deferring completely is its own failure, and a quieter one. The back tank idle lights x2 and x3 in a single
arm run at y19, which breaks the one-highlight rule everywhere else in his own art. I found that and said so.
That is the correct behaviour, and I should expect to do more of it, not less, as the measured rules in
`sprite-guide.md` accumulate.

So the target is not obedience. It is to become good enough to disagree usefully, with evidence, about any
frame including his. Until then: look first, measure second, flag what I see, and let him decide.
