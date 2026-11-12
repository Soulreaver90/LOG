# Sprite guide

How sprites work in LOG, and the rules we draw by. Every rule here was paid for by a mistake or a measurement.
The source of each rule is named, so a rule can be argued with.

> Read this before drawing or reviewing any frame. It is the standing reference. Task reports are history.

---

## 1. How the game stores a sprite

| Word | What it means |
|---|---|
| **set** | One character's whole sprite collection, picked by a set id |
| **anim** | One animation inside a set, such as idle or walking |
| **dir** | Which way the character faces: `0` down, `1` up (back), `2` left, `3` right |
| **index** | Which frame of that animation |
| **record** | One frame's packed bytes: `dx`, `dy`, `w`, `h`, `attr0`, `attr1`, plus tiles |
| **key** | The triple `(anim, dir, index)` that names one record |

Set id `N` resolves through the u32 at `rom:0x959C`, entry `N - 7`. A ROM that moved the table resolves through
its own copy. See `scripts\permanent\rom\rom_sheet.py` and `docs\research\re-sprite-decompression.md`.

### Dir 3 is usually dir 2, flipped

Dir 3 normally reuses the dir 2 frame header and draws it with the OBJ h-flip bit, `attr1 & 0x1000`. It is a flip,
not a drawing. Two exceptions:

- The front-facing anims `9, 11, 14, 17, 21` draw dir 3 as is, with no flip.
- Anim 20 in sets `56`, `59`, `157-159` has its own dir 3 frame header, so it is a real drawing.

**Trap:** counting PNGs counts drawings, not records. One PNG can serve several keys.

### One PNG can serve several keys

`art\<folder>\manifest.json` maps each PNG to a list of keys. `art_records()` in
`scripts\permanent\patches\gohan_gi.py` reads it. When two keys share a PNG and you need them to differ, the PNG
must be **split**, and the manifest must give each key its own file. `make_gi_base_v2.py` does this and checks
that the key count does not change.

---

## 2. Drawing rules

### Proportions

- Front idle body is about **13-14 px wide**. The head is about **16 px**.
- Arms are **1-2 px skin columns, close to the torso**. A 4-5 px arm reads as a sleeve.
- Draw a **turnaround first** (front, back, side) and derive every other frame from it.

Source: measured census in `docs\tasks\2026-10-30-zhack-review\style-study-report.md`. Vanilla runs wide at 19 px
body and 17.5 px head. Our old gi ran 15 and 17, which is why it read bulky.

> [!WARNING]
> **These numbers were measured on gi Gohan, who is slim. They are not a law.** Applied to Trunks on
> 2026-11-01 they made a 10 px body under a 16 px head, and he read as scrawny. The final arms are 3 px,
> because a 2 px arm is a line and one tone, with no room for form.
>
> **An outfit swap overrides this section entirely.** There the width comes from the vanilla frame, and the
> only rule is the one in "An outfit swap changes the garment pixels and nothing else".

### Colour

- Shade with **2 main tones plus a line colour**. A third tone appears only as a 1 px step.
- **Do not spread 4 tones evenly.** That is what makes a limb read as mud with no form.
- The line colour is part of the drawing. Skin lines with its own dark tone, not with black.

Source: the same census. Our set 159 spread 4 skin tones evenly and lost all form.

**Trap:** picking a ramp by pixel count picks the fill, not the role. The most common index in a garment is its
fill. The darkest index is usually its **line**, and it is only a few pixels. Map by role, never by rank.

### Silhouette

- The silhouette carries the read. Change it on purpose, and know why.
- Removing a garment **narrows** the figure. Keeping the garment's outline and only changing colours leaves the
  old bulk behind, and the result reads as the old garment in a new colour.
- **Draw the body, not the garment.** A body without a jacket has freedom the jacket hid: a real neck, and arms
  that separate from the torso. Recolouring inside the garment's outline cannot produce either.

Source: the armor redraw, then the Trunks tank on 2026-11-01. Both kept the garment outline and both lost the
neck and the arm separation.

### Find the face outline before you draw

Locate the jaw, mouth and chin **by eye on a blown-up frame** before touching a row. Write down the first body
row. Then draw from that row down.

On a 16x32 LoG frame the head runs to about row 15, and row 15 is usually jaw and mouth, not collar. A garment
collar that reaches jaw level is the garment, not the head, so it clears when the garment goes.

**Separate the head from the neck.** Vanilla puts a dark shadow band under the jaw. Keep that band. Without it
the head sits straight on the chest and the neck disappears, however wide it is. A neck of 3 px is too thin at
this scale; about 5 px reads.

Source: on 2026-11-01 I began a redraw at row 15 and painted over half of Trunks' mouth.

### An outfit swap changes the garment pixels and nothing else

This is the method. An outfit swap is the same sprite without the garment, so:

1. Build the **garment mask** from the vanilla frame, by index. Never from a part-edited file, where the indices
   are already ambiguous.
2. Change **only** the masked pixels. Everything else stays vanilla: face, chest, belt, hands, legs, boots.
3. **Prove it.** Compare your frame against vanilla over the areas you did not mean to touch, and print the
   result. Do not assume it.

A masked pixel becomes one of **four** things, never just one. Decide which before you pick a colour:

| Outcome | When | Example |
|---|---|---|
| **Bare body** | The garment lay directly on skin | The jacket sleeve over the upper arm |
| **New garment** | The new outfit covers that spot too | The tank strap |
| **Next layer down** | The garment lay over another garment, not skin | A coat hem over a trouser leg |
| **Cut to transparent** | The garment was bulk standing in open air | A raised collar, a flared coat tail |

What the old garment left exposed **stays exposed**. In vanilla the open jacket shows bare chest at x6-10 over
three rows, so the tank keeps all of it and the tank is the strap either side, not a panel across the middle.

### A garment adds bulk, so taking it off must SHRINK the silhouette

Source: the owner's three approved Trunks tank frames, measured 2026-11-01.

A pure recolour keeps a jacket-sized outline and then has to fit a bare arm, a tank and a chest inside a space
that was drawn for a jacket. The arm loses, every time. That is the whole reason my side view failed four
times and the owner had to draw it himself.

What he actually did, counted from his frames:

| Facing | Jacket px | Cut to transparent | Net silhouette |
|---|---|---|---|
| Front | 63 | 17 | -13 px |
| Side | 46 | 10 | -9 px |
| Back | 57 | 2 | -2 px |

So: **before colouring anything, decide which masked pixels disappear.** A frame where the silhouette did not
shrink at all is a finished recolour, not a finished outfit swap. Check the count and say it out loud.

Under a hem is the next layer, not air. Fill a hem pixel with trouser where a leg is below it, and cut it only
where it was flaring into open space.

### Validate a drawing rule against approved art before you apply it

Source: this is how the side walk row was caught, 2026-11-01.

Any rule that decides pixels gets run **blind over a frame the owner already approved**, and scored against
what he actually drew. Score the **role** (arm, garment, next layer, cut) separately from the exact shading,
because shading is by eye and role is structure.

My first side walk rule said "the back-most run of garment in a row is the near arm". It scored 46%. The
reason is worth keeping: in rows 18-19 the tank and the arm are **one contiguous run**, so no run boundary
exists to split them. A garment and the limb in front of it merge into a single mass, and only depth tells
them apart. Re-stated as a fixed column band read off his idle, the same rule scored 84% on role.

Under 70% on role means the rule is wrong. Fix the rule; do not hand-patch its output.

### A rule draws the frames that REPEAT. Hand draw the frames that do not

Source: the owner, 2026-11-02. > "This is why this cannot be purely numbers, you have to look, its
going to require an artistic eye as well." And: > "we ont necessarily have to use all the pixels of the
silloute, clothes change shape, we have to subjectively think about how lcothes add extra pixels."

The rule above is right and it is not enough. My down walk rule scored **81%** against his approved
stand, over the 70% floor, and it still produced four defects he caught by eye in a row: a detached
hand, no elbow, skin over the sword hilt, and a recolour where a removal was needed. I answered each by
patching the rule, five rounds of it, and each patch moved the defect somewhere else.

**The score was not lying. It was answering a different question.** It measures one still frame against
one still frame. It cannot see a limb that wanders between frames, a shape that reads wrong at 1x, or a
pixel that is locally correct and anatomically absurd.

So split the work before writing any rule:

| Frames | How to draw them | Why |
|---|---|---|
| Frames that REPEAT an approved frame | copy his rows in whole | They are his art. Re-deriving them can only lose |
| Frames a rule scores **well above** the floor | the rule, then look | The structure genuinely repeats |
| Swing extremes, foreshortened limbs, anything with gear | **by hand, pixel by pixel** | Nothing repeats, so there is nothing for a rule to generalise from |

In this cycle that split was: walks 1 and 3 are byte identical to the stand's vanilla, so they are his
rows copied, zero pixels drawn. Walks 0 and 2 share no row with him, so every pixel is a hand call in an
explicit dict with an assert that each key is inside the garment mask.

**Write the hand drawing as a dict of (x, y) to index, never as a grid.** The assert that each key is a
masked pixel is what keeps a hand drawing honest, and it is the same guarantee the mask-driven rule gave.
You lose the rule, not the proof.

**The tell that a rule has run out of road:** you are patching it for the third time, and each fix moves
the defect rather than removing it. Stop and draw the frame.

### A gap in the garment does not tell an arm from a coat tail

Source: `set:128` anim 1 dir 2 frame 0, found 2026-11-01 by reading the frame out of a built ROM.

I added a rule that the arm is the **first contiguous run** of garment at or behind the arm band, so that a
coat tail flaring further back would not be mistaken for his arm. In the walk frame where his arm has swung
back, the arm sits at x12-14 with a gap at x10-11. The rule stopped at x9. The sleeve was erased as a tail,
and **his hand was left drawn but unattached to his body**. Seven pixels, and every automated check passed.

Two rules that both look right and are both wrong on their own:

| Rule | Fails on | Score against his approved idle |
|---|---|---|
| The arm is the first contiguous run | A swung arm, which leaves a gap | amputates it |
| The arm is whatever has a hand below it | An arm hanging to the hip, ending in no visible hand | 50% |
| A plain column band, no contiguity test | nothing found yet | **84%** |

The contiguity test was solving a problem that did not exist, and caused one that did. The swung arm was
**already inside the band**. Prefer the simpler rule, and make a new restriction prove it fixes a real frame
before you keep it.

**The check that catches this class:** count bare skin per frame across an animation row. The arm is the
largest skin area in a sleeveless side view, so a frame whose skin count is half its neighbours' has lost an
arm. Walk 0 read 10 px against 21 to 24 everywhere else, and that number is what sent me looking.

### A walking figure has TWO arms, and the other one swings forward

Source: the owner, looking at stills on 2026-11-01, after my checks had all passed.

> "the issue with frame 2 is the closest arm, its drawn over with gray sprites"
> "frame 4 has black tank drawn over the farther arm"

My rule knew about one arm, the one at or behind the column band. In a standing pose that is true. In a walk
it is true for **half the cycle**: the other arm swings forward into LOW x, precisely where the rule says
"not arm". So the forward sleeve fell through to whichever branch came next, and was painted as something
else, silently and differently in each frame:

| Frame | Where the forward sleeve was | What the rule painted it |
|---|---|---|
| walk 0 | x3-6, rows 20-23, above the hand at x0-2 | trouser grey, because it was below the belt row |
| walk 2 | x3-4, rows 18-22, above the hand at x0-3 | black tank, because it was on a chest row |

Both passed every automated check I had, including the silhouette, the jacket census and the skin count,
because the skin count only notices an arm that vanished, not one that moved and was overwritten.

**This one does not become a rule.** I tried: flood the garment outward from the bare skin of a hand, and
call what it reaches a sleeve. It leaks, because the tank and the sleeve are a single contiguous garment
mass. Depth separates them and nothing in the frame encodes depth. That is the same wall as the original
side view.

So: **before drawing any walk frame, find BOTH hands in the vanilla frame and trace each sleeve back to its
shoulder by eye.** Write down where both arms are, then draw. The hands are already bare skin in vanilla, so
they are the one landmark that is never ambiguous.

### A SLEEVE is bulk too. Measure the arm against his, never against the sleeve

Source: the owner, 2026-11-01. > "the farther arm in the back, you basically filled the frames of the
jacket making his arm thick"

I had written "a garment adds bulk, so removing it must shrink the silhouette" and then applied it only at
the collar. A sleeve is bulk in exactly the same way. Filling a sleeve's outline with skin gives a thick,
boneless arm.

His approved idle, measured. This is the reference for any arm in this set:

| Row | Jacket sleeve | HIS bare arm |
|---|---|---|
| y16 | 7 px | **3 px** (he cut 4) |
| y17 | 7 px | **3 px** |
| y18 | 6 px | **4 px** |
| y19 | 6 px | **4 px** |
| y20 | 6 px | **3 px** |
| y21 | 5 px | **3 px** |

**A bare arm in this set is 3 px, 4 at the widest.** A sleeve is 6 to 8. So converting a sleeve means
keeping a 3 px band along the line from the shoulder to the hand, and cutting the 2 to 5 px of slack around
it. My frame 4 back arm was 5, 7, 8 and 5 px, with nothing cut at all.

**The check:** per row, per arm, count the bare-skin run that is not a hand. More than 4 and it is a filled
sleeve, not an arm. Counting total skin per frame does NOT catch this, because a thick arm raises the count
and a lost arm lowers it, and both can land near the right total.

### An accessory under the garment is continuous. Reveal it where the garment hid it

Source: the owner, 2026-11-01, on the Trunks tank side row.

Trunks wears a cyan sword baldric across his chest, `0x4D` and `0x47`. The strap does not stop and start,
but **vanilla only draws the parts the jacket does not cover**, so it appears as one or two stray pixels per
frame and reads like noise. Take the jacket off and the hidden run belongs back on the body.

The trace that settled it. Set 128, side row, at `x7 y20`:

| Frame | Vanilla there | Why |
|---|---|---|
| walk 2 | `4D` strap | nothing covers it, so vanilla draws it |
| idle, walk 0, walk 1, walk 3 | `51` jacket | the jacket covers it, so vanilla hides it |

So walk 2 is the proof the strap passes through that pixel, and the other four get it back.

**The exception, and it is what makes this a rule and not a rewrite.** Reveal the accessory where the
GARMENT hid it. Do not reveal it where a LIMB is in front. In side walk 0 his arm swings forward across the
chest and lands on `x5 y19`, which is a strap pixel in every other frame. It stays skin: an arm in front
still hides what is behind it.

**How to use it:** list the accessory's pixels across the whole animation row first. The union of them is
the strap's real path. Then, per frame, ask of each missing pixel whether the garment or a limb was on top.

**Confirmed again in the down row, 2026-11-02.** The scabbard's silver chape `09` is at (12,23) in down
walk 0 and (12,22) in walks 1 and 3. Down walk 2 has NO chape at all, because that frame swings the right
arm forward over x12-x14 rows 18-22. Same rule, second accessory, other animation row. The useful part is
the test: a count of the accessory's index across the row is expected to come back UNEVEN, so an even
count per frame is the thing to suspect. I had written in a report that the chape was in every frame, and
counting the bytes is what caught it. Look at the picture to judge the drawing, and count the bytes before
stating a fact about it.

### An arm swung forward still needs a shoulder

Same frame, next pass. After thinning, side walk 0's forward arm began at row 20 and sprouted from his hip,
because rows 17 to 19 were still tank. In a side view a forward-swung arm passes **in front of** the torso,
so those rows are arm and the tank takes the 3 px behind it. Trace the limb from shoulder to hand and check
it is unbroken before calling the frame done.

### First ask what the garment HIDES, and what is nearest the viewer

A garment mask says which pixels change. It says nothing about **what is underneath them**. When a garment
covers the boundary between two body parts, the mask cannot tell you where that boundary is, and the swap
stops being a recolour and becomes an anatomical reconstruction.

Before converting a single pixel, answer in writing:

1. **What body parts does this mask cover?** Torso only, or torso and a limb together?
2. **Which of them is nearest the viewer?** The nearest one is drawn on top and takes the most area.
3. **What is the point of this swap?** A sleeveless top exists to show arms. If the result does not show more
   skin than before, the swap has failed whatever else is right.

**The depth rule:** in a side view the near arm hangs over the **back half** of the torso silhouette, because
the shoulder joint sits toward the back of the chest. It is the closest thing to the viewer and the largest
skin area in the frame. In a front or back view both arms sit beside the torso and overlap it very little.

**A raised collar stands in front of something, and it is not always the body.** In the back view the collar
at row 13 shows through a gap in the hair, with hair at x3-5 and x11 either side of it. Removing it closes the
hair's bottom edge. Filling it with torso puts a shirt on the back of his head. Ask what the garment is
standing in front of, row by row, before converting it.

**The head fills the same box in every facing. Measure it against the front.**

| Facing | What fills the head box |
|---|---|
| Front | hair to y12, then face to y15 |
| Back | **hair all the way to y15**, because there is no face |

Vanilla's back shows hair only to y13, because the raised collar covered the rest. Remove the collar and the
hair must reach y15 to match the front, or the head is two rows short and the body starts too high. Measure
the front's head box first and make the back's hair fill it. On 2026-11-01 I stopped at y13 and put nape and
tank in rows 14-15; the owner's fix was "I referenced the front, there is some sort of symmetry".

**On a back view the garment is nearly all hidden, so draw almost none of it.** The hair covers the top, the
scabbard covers the middle, the arms take both sides. In the finished frame the tank is **7 px**. My version
drew 12 px of tank plus 5 of nape into space that was already occupied. Count what is left after hair, props
and limbs before deciding how much garment to draw.

**A scoop neck shows a sliver of bare back.** Three skin pixels at row 16 sit between the hair above and the
tank below. Skin is form independent, so that sliver copies to both forms unchanged.

**Revealed hair is form specific, so it is head, not body.** Base hair is `0xE5` and Super Saiyan is `0x14`.
A collar gap filled from a single constant gives one form the other's hair colour, and the one-body check
will not catch it, because the error is inside the rows the check treats as head. Fill it from that form's own
neighbouring hair pixel, and move the head and body boundary below the filled row.

**The check, and it is mechanical.** For a sleeveless swap, count skin against garment inside the mask:

```
py -3.14 -I scripts\permanent\rom\sprite_guard.py check <vanilla> <edited> --garment ... --body-from 15
```
then compare skin and garment pixel counts in the changed set. In a SIDE view of a sleeveless top the arm
must win. If the garment outweighs skin, the arm has been buried and the frame is wrong.

Source: the Trunks side view, 2026-11-01. Vanilla's front shows the jacket as two side panels with the body
between them, so the front was a recolour and it came out close to right. Vanilla's side shows one blue mass
covering torso and near arm together. I read that mass as torso four times running, filled it with tank, and
gave the arm a 2 px strip. The owner drew it from scratch and his verdict was the diagnosis: "its a sleevless
tank top with exposed arms". In his frame the arm is the largest skin area. In all four of mine it was buried.

### Drive the swap from the mask in code, never from a hand written grid

Write a function that takes one garment pixel and returns what it becomes. Loop the mask over it. Then every
non-garment pixel keeps its vanilla value **by construction**, and the count of changed pixels must equal the
mask size exactly. Print both and compare them.

```python
def new_index(x, y):          # only garment pixels ever reach this
    if y <= 17 and x <= 4:    # the near arm the sleeve hid
        return SKIN[x]
    if y <= 19:               # the torso above the belt
        return TANK
    return TROUSER            # the hip under the jacket skirt
```

A hand written grid re-types the rows around the garment, so it invites redrawing them. On 2026-11-01 the
Trunks side view took four failed passes that way: each one moved the arm, re-sited the belt or changed where
the tank ended, and the owner's verdict was "I dont know why you are finding this very difficult". Rewriting
the same swap as nine lines of mask-driven code produced 44 changed pixels for a 44 pixel mask, and it was
right the first time.

**The tell that you are redesigning:** you are deciding something the vanilla frame already decided.

Source: on 2026-11-01 I repeatedly drew the tank over the chest. Each pass made it worse, and the owner had to
point at the same three pixels twice before I compared against vanilla and found them.

### Separate two skin areas with the darkest value you have

Where a bare arm sits beside a bare chest, both are skin, and they merge. Whatever lies between them must carry
the separation. A mid grey is not enough. Use black.

A 1 px black strap reads as cloth, separates the two, and costs no chest. It is what a tank actually looks like.

### Shade a LIMB with three tones and one highlight at a constant offset

Skin has five palette entries. In the side view vanilla uses three: across the five side frames it draws `17`
dark 152 times, `13` mid 81 times, `11` lit 35 times, `12` once and `15` never. Work in `17`, `13` and `11`.
The front and back views do use `15`, 7 times in the approved front idle alone, so "never `15`" is a side-view
fact, not a palette fact. Index `18` sits inside the skin ramp and is RED. It is never skin.

Two rules, each with its own source. They cover limbs. A chest is not a limb: the approved front idle shades
its chest `M L M L M` across y17.

1. **One highlight per limb run.** Of 49 vanilla limb runs, not one carries two `11` pixels. Two highlights in
   one run is the clearest sign of colour dropped in by hand. Source: vanilla.
2. **The highlight holds a constant offset from ONE edge of the run.** Not a constant x. A limb that slants
   keeps the highlight the same distance in from its chosen edge, so measuring in absolute x calls every
   diagonal arm broken. Source: the approved front idle, whose right arm sits at offset 0 from its inner edge
   for five rows, and whose left arm does the same on its own inner edge for four.

Which edge is a per-limb choice, so decide it once and hold it. Both front arms light the edge nearest the
body. Trunks' side walk 2 lights the far edge instead, because the hand row directly below it is lit there.
Follow the vanilla pixels you are joining onto.

A bare upper arm carries the highlight its whole length. A wrist or a shadowed crossing may drop it, and
vanilla drops it often, so a gap low on a limb is not automatically a fault. Do not take the hand statistics
as the arm budget: every vanilla skin run below the jaw is a hand or a cuff 2 to 4 px wide, 69% of them carry
no highlight at all, and applying that ratio to a 3 px arm strips it. Measure an arm against an approved ARM.

Not every piece of approved art obeys this. The back tank idle lights x2 and x3 in one arm run at y19, which
breaks rule 1. It is a known defect, not a counter-example.

Source: on 2026-11-01 the owner said he had "randomly splashed skin colors". The hanging arm lit x9, x10,
x10, x9, x9 on five consecutive rows. Not one pixel was the wrong colour. The offset wandered, and a
wandering highlight is what reads as splashed.

### A dark edge is an outline, but so is everything else dark

Before you darken a skin pixel at the edge of a limb, read the REAL index of its neighbour. Black tank `01`,
cyan baldric `4D`, scabbard orange `23`, and trouser grey `0D` and `0F` all outline a limb already. Only a
pixel that sits against clear `00` needs its own `17`.

Count every non-skin neighbour as absent and you add an outline column to an arm that already had one. A
3 px arm then becomes a 1 px lit line between two dark edges. That is the thick-arm mistake running backwards.

### LOG is chibi: the head is half the figure, and the TORSO is what shrinks

Measured off the approved Trunks side idle, which is 30 rows of real pixels:

| Segment | Rows | Share of the figure |
|---|---|---|
| Head top to chin | 13 | **43%** (a realistic adult is about 13%) |
| Neck to hip, the whole torso | 4 | 13% |
| Hip to knee | 4 | 13% |
| Knee to ankle | 5 | 17% |
| **Hip to ankle, the whole leg** | **9** | **30%** |

The head alone is as tall as the entire body below it, about 2.3 heads to the full figure.

**The trap is the obvious inference.** "Chibi" suggests short limbs, so the instinct is to shorten the legs.
The measurement says the opposite: the legs keep 30% and the TORSO is crushed to 13%. The whole leg is more
than twice the torso. Shorten the legs to suit a big head and you get a dwarf, not a chibi.

### The hip joint is at the BELT line, not where the legs separate

The belt sits at row 20 and the legs only split apart around row 23, because the thighs touch at the top.
Anchor the hip to that split and it lands two rows low, which lengthens the torso and shortens both legs at
once. Every proportion below the waist then follows the error.

Source: on 2026-11-01 I placed the hips at y23 against the owner's y21. Every joint of mine sat on a real
pixel and the depth order was correct, so neither of my checks could see it. He saw it at a glance.

### Name the ACTION before you look at a pixel

This is the rule I did not have, and every pose failure on 2026-11-01 and 2026-11-02 came from not having
it. I worked bottom up: find a pixel, put a joint on it, join the joints. That cannot work. A pixel does
not know whether it is a hand or a hem, and a joint graph built that way has nothing to be wrong against.
The owner works top down. He knows it is a walk and which phase it is, so he knows what the body must be
doing before he looks, and then he finds that in the picture.

**The action is recorded, not guessed.** RE-BIBLE lists the anim numbers: 0 stand, 1 walk, 2 hurt, 3
knocked down, 4 idle variant, 5 punch, 6 to 8 melee, 9 power up, 10 knocked out, 11 lift arms overhead,
12 swim or fly depending on the set, 13 run, 14 crouch, 16 to 19 specials and charge, 20 fly, 21 revert,
22 stand 2. Look the anim up first. It tells you the action free of charge.

Work in this order, and write each step down:

1. **Name the action, the direction and the phase.** Which anim, which dir, which frame in play order,
   and whether that frame is an extreme or a pass.
2. **Say what the body must be doing, before looking at a single pixel.** For a walk: one leg forward and
   one back, arms opposite the legs, head highest at the pass. For a kamehameha: both arms to one side,
   weight back, torso turned. For a knockdown: the body axis is not vertical at all.
3. **Find the BODY AXIS.** See the next rule. A walk hides this step because the axis is the screen
   vertical. Nothing else does.
4. **Now locate the joints.** Anchor each one along the body axis from the proportion table, then take its
   across-axis position from that limb's own pixel mass, on the mass's centre line.
5. **Compare what you found against step 2.** The disagreement IS the finding. Never quietly adjust one to
   fit the other. When the art does not do what the action requires, that is a fact about the art and it
   gets reported: in the Trunks side walk, frames 1 and 3 share one arm pose, so the pass frames do NOT
   put the arms in opposite phase.
6. **Render it, play it, and look.** That is the last test and it belongs to the eye.

### Find the BODY AXIS first. The screen's vertical is not the body's

Crown to crotch is the body's own axis. For a standing or walking figure it runs straight down the screen,
so the whole question is invisible, and a rule written only off a walk will read "fraction down the
screen" and then break the first time the character lies down, crouches, flies or is knocked over.

Every proportion below is **along the body axis**, measured from the crown. Nothing below is a screen
measurement.

To find the axis on a frame: take the head mass and the pelvis, and draw the line between them. Lying
down, that line is near horizontal and the proportions still hold along it. Flying prone, the same. For a
crouch the axis bends at the hips, so the figure needs two axes, one for the torso and one for the legs,
and every limb is measured against the one it hangs from.

### Proportions along the body axis

Measured from the owner's own five hand drawn skeletons for the Trunks side walk, 2026-11-02. Each value
is a fraction of the figure's length along its axis, which for that row is the silhouette's lowest row
minus its highest. It carries no palette index, no pixel count and no species, so it ports: measure the
new sprite, multiply, and you have the anchors, for a Namekian, a child or an adult.

| Joint | Fraction along the axis from the crown | Spread over 5 frames |
|---|---|---|
| Head point | **0.37** | 0.37 to 0.40 |
| Neck | **0.51** | 0.49 to 0.52 |
| Shoulders | **0.51** | 0.49 to 0.53 |
| Pelvis | **0.62** | 0.62 to 0.64 |
| Hip | **0.63** | 0.62 to 0.66 |
| Knee | **0.74** | 0.72 to 0.77 |
| Ankle | **0.86** | 0.80 to 0.92 |

Each holds to about two hundredths across a whole walk cycle. The body does not change length; the limbs
swing across it. So **anchor along the axis from this table, and read the across-axis position from the
frame**. I did the reverse, taking the across-axis position from pixel extremes and letting the other
float, which is why my joints wandered between frames.

The neck at 0.51 is the chibi rule restated: the head fills the top half.

> [!WARNING]
> These came from one character in one action. Treat them as the starting estimate for a new sprite, then
> check them against that sprite before trusting them. A child is a larger head and a shorter leg, so its
> knee and ankle sit lower in the fraction. Measure, do not assume this table transfers unchanged.

### Which bones hold their length, and which do not

Same source, as a fraction of the axis length. The spread column is the whole point.

| Bone | Median | Spread | Use it as |
|---|---|---|---|
| Spine, neck to pelvis | 0.122 | 0.016 | a constraint |
| Head to neck | 0.133 | 0.022 | a constraint |
| Forearm | 0.094 | 0.015 | a constraint |
| Thigh | 0.133 | 0.026 | a constraint |
| Upper arm | 0.102 to 0.128 | 0.050 to 0.102 | NOT a constraint |
| Shin | 0.158 to 0.195 | 0.072 to 0.074 | NOT a constraint |

**The stride is carried by the shin, not by the thigh.** The thigh and the spine hold their length through
the cycle. The shin grows by half again between the idle and the stride extremes, because the artist moves
the foot further than a rigid leg allows so the stride reads at 1x. Hold every bone to one length and you
flatten the thing that makes it a walk.

**The unstable bones are the ones the owner said he guessed.** He called his obscured limbs and his bends
anatomical judgements rather than readings. The upper arms and the shins carry the widest spread in his
own data. That agreement is the useful part: the numbers are tight where his drawing is confident and
loose where he was inferring. Never quote a loose number back to him as a measurement.

### A joint is INSIDE the limb. Never put one on the silhouette edge

On 2026-11-02 I placed a wrist at x1 because x0-1 was the leftmost skin pixel in the frame. That pixel is
the outer edge of a hand. I placed both ankles on boot centroids, which are the middles of the feet. I
took a shoulder from the widest row of the torso, which is the silhouette and not the ball of the joint.

A boundary is always further out than the joint inside it, so every one of those errors pushes the same
way. The figure comes out too wide and the upper arm comes out too flat. A copied shoulder plus an
outermost hand pixel draws a level arm, and a level arm reads as a dance.

**Take the joint off the limb's centre line, inset from the tip.** The wrist is up the arm from the
fingertips. The ankle is at the top of the boot. The shoulder is inside the torso mass.

### Work at a larger scale, then come back down

A 16x32 sprite is too small to measure geometry on directly. A limb is 2 to 3 px wide and it touches the
torso, so anything that reasons about shape runs out of room. Upscale with NEAREST first, which adds no
information at all, do the geometry there, then divide the result back down. The answer lands at sub-pixel
precision, which is what a joint needs anyway.

Three places this has already decided the outcome:

- **Centre lines.** Thinning the silhouette at 1x destroyed the figure: the arms vanished, the idle kept
  three branch ends, and walk 1 kept one. The same thinning at 8x gives a clean graph in every frame, with
  a spine, two arm branches and two leg branches. Same algorithm, same pixels, only the room changed.
- **Reading the owner's pose sheets.** He draws at the export resolution, so his lines are thinner than a
  sprite pixel. I sampled one point per sprite pixel and reported his five complete skeletons as 41
  scattered dots. Read the cell whole.
- **Aligning a screenshot to the sprite grid.** Recovering the grid from the full size shot fits at 96%.
  Downsampling first throws away the evidence that makes the fit possible.

The rule generalises past sprites: **never reduce the data before the measurement, only after it.**

### Structure comes from the silhouette, not from knowing the action

Writing down what the body does in every anim, for every character, is unbounded work and it would fall on
the owner. It is also unnecessary. Four things hold in every pose of every character:

1. **The body graph never changes.** The same joints with the same connectivity, for a Namekian, a child
   or an adult. Only the lengths and the angles differ.
2. **A limb is a connected run with a centre line**, in any pose, under any palette.
3. **The silhouette's extremities are limb tips.** The points furthest from the body mass are a hand, a
   foot or the head, whatever the character is doing.
4. **A bone can only be drawn shorter than it is, never longer.** So its true length is its MAXIMUM across
   all frames, and any frame where it comes up short is foreshortened, which means that limb points toward
   or away from the viewer. Depth falls out of length, with no depth cue needed.

So the method is: thin the silhouette at scale, read the branch ends and junctions, fit the fixed body
graph to them using lengths learned from the character's own most extended frame, and take depth from
which bones came up short. The action is an OUTPUT of that fit, not an input to it.

> [!WARNING]
> Two gaps remain, both found by testing it on the Trunks side walk on 2026-11-02.
> Spiky hair produces false limb tips. Trunks' hair gives four branch ends above the shoulders. The fix is
> to find the head mass first, at one end of the body axis, and discard tips inside it.
> Equipment branches too. The silhouette carries the sword, the scabbard, the baldric and the hair, and
> each grows its own branch. The idle's branch end at x13, y23 is the SCABBARD TIP, not a hand.
> DISPROVEN, 2026-11-02, TWICE. First: that a palette ramp is a run of indices sharing a high nibble. It
> holds for skin (11, 13, 17) and for the scabbard (21, 22, 23, 25) and it FAILS for Trunks' hair, which is
> 62, 64 and E5, one visual ramp across two nibbles. Second, and this is the one that matters: that a limb
> tip can be confirmed by what it is MADE OF at all. Grouping by hue instead of by nibble does not save it.
> In `set:128`, index 02 is the eye white AND a hair highlight, 4F and 51 are jacket AND iris, 21 is belt in
> the front view and scabbard in the back, and the greys are trousers AND sword metal. No grouping of
> indices separates those, because the artist reused the ramps. See the next rule for what does work.
> The junctions land low. Thinning put the shoulder junction at y19.9 and the pelvis at y21.9, against the
> owner's y17.2 and y20.7. A huge head drags the axis down. Fit the graph to the junctions, do not take
> the junctions as the joints.

### Carry limb IDENTITY across frames. Do not rebuild the skeleton per frame

An animation is one body in several poses, and a bone keeps its identity through all of them. I rebuilt
every joint from each frame's own pixels, so the same joint moved between frames for reasons that had
nothing to do with motion. That incoherence between frames is what reads as dancing.

The owner's sheets solve it by construction: one colour per bone, the same colour in every frame. Reading
them back gives limb identity for free, and it is how the leg swap in this cycle was finally proved. His
pink leg's foot is on the screen left in the idle and in frames 0 and 1, and on the screen right in 2 and 3.

With no such sheet, find one feature that marks a single limb and track it. In this row the lit boot top
does it: it appears on one boot per frame and follows that leg. Note what it does NOT say. It sits on the
far leg in walk 0 and on the near leg in the idle, so it is an identity tag and not a depth cue. I lost a
round treating it as one.

### Check a pose with evidence you did not build it from

My audit asked whether each joint sat on a non-background pixel. Every joint came FROM a pixel, so it
passed every time and could never fail. A check built from the build's own evidence is not a check.

Three that are independent:

- **Does the bone lie ALONG the limb's centre line, or across it?** A bone that crosses its limb is wrong
  however good its endpoints are.
- **Play it.** A still frame hides a joint that slides, a leg that never crosses, a pelvis that never
  drops. Animation is the only review that catches those.
- **Does it look correct?** Render it and look, head to foot, before measuring anything. That test is the
  owner's, and asking him early costs far less than asking him late.

**Where a check STARTS decides what it can find.** On 2026-11-02 I checked each arm with a flood of skin
from the shoulder to the vanilla hand, and started the flood on a pixel of the arm itself. Walk 2 had no
deltoid at all, its arm hung unattached under the sword hilt, and the check passed, because the start was
inside the thing it was meant to validate. Start on the BAND row, which is a landmark the drawing did not
invent, and the same check fails the same frame.

The general form: **a check that starts inside its own subject can only confirm it.** Anchor every check
on something the drawing did not choose.

**A direction of travel is independent evidence; a position is not.** Once the arms were hand drawn, the
approved pose became a real check again, because nothing in the art came from it. Drawing the pose over
the finished frames and asking whether each bone lies along its arm caught nothing that round, which is
the point: it was free to fail and did not. The same overlay while the arms were GENERATED from the pose
was worthless.

### Reading an owner pose sheet

He exports from Piskel as a grid of cells, one cell per frame, each cell the sprite at a whole number
zoom. The pose is drawn at the EXPORT resolution, so its lines are thinner than one sprite pixel.

**Read the cell whole. Never sample it per sprite pixel.** On 2026-11-02 I sampled each block's centre and
reported his five complete skeletons as 41 scattered dots, then asked him whether they were joints or
unfinished bones. The drawing was complete. My sampling was not.

`scripts\one-time\2026-11-01-trunks-side-walk\read_owner_pose.py` does it properly: group the ink by exact
colour, take each colour's two extreme ends as one bone, then chain the bones through their shared ends
into named joints. `verify_owner_pose.py` draws the result back over his ink, which is the only way to
prove the reading before anything is built on it.

### Name every region by eye, THEN place the joints

This is the method. Everything above it in this file is support for it.

Four automatic body finders were tried on the Trunks side walk and all four failed: a high nibble palette
ramp, a hue cluster, a skin plus ground filter over the medial axis branch ends, and motion across the
cycle. They failed for one reason. **The artist reuses palette ramps, so no index, hue or ramp names a
part.** The eye white is also a hair highlight. The iris blue is also the jacket. The belt orange is also
the scabbard. The trouser grey is also the sword. A filter over colour cannot separate what the colour
does not separate.

What works is looking. Render the frame at 30x with the palette index printed in every cell, look at it,
say what each shape is, and write it down one letter per pixel. That takes a few minutes a frame and it is
exactly how the owner reads a sprite. It is not a fallback. It is the primary instrument, and the code
around it exists only to make the picture big enough to read and to record the answer.

The procedure, for any character and any anim:

1. **Render big, with indices.** `look_close.py` in the side walk folder, or `down-walk\show.py`.
2. **Write a region map**, one letter per pixel, into a `regions.txt` next to the frames. Letters name
   parts, never colours: hair, face, eye, neck, chest, garment, belt, arm, hand, trousers, boot, gear.
   Give the second arm and the second leg their own letters, so limb identity is in the file.
3. **Check the transcription**, not the reading: every lit pixel carries a letter and no dead pixel does.
   `show_regions.py` prints both counts. It cannot tell you an arm is really a scabbard. Only you can.
4. **Render the map back** over the frame and LOOK at it, in three panels: the sprite, the naming, and
   body against gear. A wrong call is obvious in the third panel and invisible in a table.
5. **Place the joints from the map**, on each region's centre line, inset from its tip.

On 2026-11-02 this read both of the idle's hands correctly, including one whose arm is entirely hidden
inside the torso and which shows only as a 2x4 blob at the hip. The owner's own skeleton puts that wrist at
x3.17, y22.17 and the other at x8.00, y23.83. Both landed. No colour rule found either of them.

### Identify gear in the view that does not hide it, then track it into the views that do

Equipment is the hardest thing to tell from a limb, and it is also the easiest, as long as you look in the
right frame. A character has a front, a back and a side view of the same stand pose. The gear is in all
three, in the same place on the body, and at least one of them shows it unobstructed.

So inventory the gear ONCE per character, from the clearest view: each piece, its indices, and where it
attaches. Then find each piece in every other frame, or state plainly that it is hidden there.

Trunks, worked through: the back view shows the whole sword, hilt high on his left shoulder in grey, and
the scabbard running diagonally down across the back in orange with grey bands. The front view confirms
the hilt, two grey pixels clearing his shoulder at x0-x1. The side view shows the scabbard behind the hip
and NO HILT AT ALL, because the hair mass fills exactly the rows where the hilt would sit. Without the
back view, those side view orange pixels are just as likely to be a sleeve.

> [!WARNING]
> A piece of gear that is hidden in a frame is not absent from the body. Say "the hilt is behind the hair
> in this view", never "there is no hilt". The second sentence licenses drawing a figure with no sword.

**Open the reference frames and copy the gear's SHAPE, not just its position.** Source: the owner,
2026-11-02, "look at the reference images to have an idea of what the hilt is supposed to look like",
then "always reference the images". I had this section already and still drew the down walk 0 hilt from
its vanilla anchor alone, without opening his approved back or front frames. The result was a lone
highlight floating above two flat greys, and he called it messy.

What the frames actually say, and none of it is guessable from one frame:

| Frame | What it shows |
|---|---|
| His approved BACK | the whole sword: grip `0D 0B 0D` and `0B 09 0B`, then a guard, then the orange scabbard running down across the back |
| His approved FRONT | the hilt alone: grip down x0, a black outline stepping in, then the guard as **`0D 0B 0D` over `0D 0B`** |
| Vanilla, any frame | 1 to 2 px of guard, wherever the garment happens not to cover it |

So the guard is a **3 px crossguard with a bright centre, over a 2 px row that steps outward**, and `09` is
a third, brighter grey that exists for the metal highlight. A reveal that gets the position right and the
shape wrong still reads as noise. Open the frames, read the shape, then place it on this frame's anchor.

### A down walk is not a side walk turned ninety degrees

The side walk is the easy case and a method tuned on it will break on everything else. The difference is
not the angle, it is where the motion goes.

| | side walk (dir 2) | down walk (dir 0) |
|---|---|---|
| The stride runs | across the screen | into the screen, at the camera |
| Legs at the extremes | furthest apart | ONE column, the back leg hidden behind the front |
| Legs at the pass | overlapping | TWO columns, side by side |
| Arm swing shows as | position | LENGTH, because a swung arm foreshortens |
| Feet drawn | both | one, in `set:128`; the other has no pixels |

Read depth from LENGTH, never from a depth cue. A bone is never drawn longer than it is, so its true
length is its maximum across the cycle, and a frame where it falls short is a frame where that limb points
at or away from the viewer. In the `set:128` down walk the screen-right arm measures 3.4 px shoulder to
wrist in frame 0 against 6.7 px at its longest: half length, so it is swung out of the screen plane. Frame
2 does the same on the other side. That is the whole arm swing, and no colour or silhouette rule sees it.

Foreshortening gives you the AXIS, not the SIGN. Short means out of plane, and BOTH extremes project
short, so it never says toward or away.

**The sign comes from HEIGHT: nearer is drawn lower. Use that one rule for hands and for feet.** In the
`set:128` down walk frame 0 the screen-left hand sits at y23.8 against y19.5 on the right, so the
screen-left arm is forward; the lower ankle puts the screen-right leg forward. Opposite sides, as a walk
requires, and frame 2 mirrors it.

> [!WARNING]
> On 2026-11-02 I read the feet by height and the hands by "raised means forward" in the SAME pose. That
> put an arm and a leg forward on the same side, and I was about to report the vanilla art as ipsilateral.
> It was not a finding about the art. It was two conventions in one skeleton. When a pose contradicts
> anatomy, suspect your own rules before you suspect the artist.

At the pass both hands hang level and the art calls no side. Say "level, no call" there. A tie broken by a
hundredth of a pixel is false precision, and it will flip the moment a joint moves.

### Below the waist, the outer end of a garment run is the TAIL, not the arm

Source: the Trunks tank down walk, 2026-11-02. The owner, four times: "oddly disconnected",
"wheres the elbow", "why is the arm not curved properly like a human", and
"In some parts you correctly removed the jacket, and others you recolor".

The rule read off his front stand was "the arm is the 3 px at the OUTER end of each garment run".
It scores 81% on that stand because his arms hang straight down beside a closed jacket. In down
walk 0 it drew the arm down the COAT TAIL: vanilla has jacket at x1-x3 for rows 21-24, and the
bare hand at x3-x6 for rows 23-25. The tail is further out than the hand. So the rule walked the
forearm away from the hand it was supposed to end in, and the hand read as detached.

**A jacket run below the waist can be a sleeve, a tail, or both end to end. Nothing in the run
says which.** What does say is the hand, which is already bare skin in vanilla. Draw the arm
toward the hand, and cut whatever is outboard of it.

Three checks, and none of them is built from the pose the arm was drawn from:

- **A 4-connected skin path from the deltoid top to the vanilla hand.** Start it on the BAND row,
  never on a pixel of the arm. A start taken from the arm passes a frame whose shoulder is missing.
- **Per row, is the SKIN run narrower than the garment run it replaced?** A garment adds bulk, so
  equal width is a recolour. Over a whole frame his front cuts 17 of a 63 px mask, about 27%.
- **Does the outer edge walk?** His arm moves out 3 columns over 7 rows, about one every two rows.
  An arm that holds one column for six rows is flat, and a flat arm does not read as a Z fighter.
  The elbow is where that walk turns around, and it is at least 2 rows tall. A 1 px elbow reads as
  a kink.

  **How deep the bow goes, calibrated by the owner on 2026-11-02.** Where the hand sits further IN
  than the elbow, so the arm must bow out and come back, **one column held for three rows is right
  and two columns is too much**. He called 3 3 3 2 1 2 3 "a bit much" and accepted 3 3 3 2 2 2 3.
  A bow is sustained, not deep. Where the hand keeps going out, as in his own front stand, the edge
  just keeps walking and never turns around.

**Where the arm gives a column back, the tank and the baldric take it, not more arm.** An arm swung
back sits behind the torso, so it shows LESS skin than its sleeve did, and the 2 px it releases
become a wider black tank edge. Widening the skin instead is the thick-arm mistake again.

### Slope the shoulders

Width must step up gradually: face, then shoulder, then deltoid. A jump straight from face width to full
shoulder width makes the shoulders look stuck on. Removing a collar creates exactly that jump, because the
collar was the step.

### A garment needs a footprint and an outline

Before recolouring, find the area the new garment must fill. In vanilla the **visible chest between the jacket
panels shows exactly where the tank belongs**, and how large it must be.

Give the garment its own outline. A fill with no outline at the same value as a neighbouring garment is lost,
and so is a pure black fill, which reads as a hole at 1x rather than as cloth.

### One body per character

Forms of one character share **one body**. Only the hair and the eyes change between forms.

Draw the body once. Compose each form as **form head over shared body**, then prove rows below the neck are
byte-identical across the forms. `gi_one_body.py` does this for sets 158 and 159.

**Trap:** vanilla does not always obey this. Vanilla sets often differ by a pixel or two in the body between
forms. When we adopt one body we drop those differences. State what is dropped. Do not ask whether to drop it.

---

## 3. Process: how to not spend the owner's eye

The owner's eye is the scarcest thing in this project. Spend it on judgement, never on catching mistakes a
script can catch. On 2026-11-01 one Trunks frame took nine passes and seven owner corrections. Most of them
were avoidable, and this section is what they cost.

### Pre-flight: run these BEFORE drawing a pixel

Source: the Trunks tank down walk, 2026-11-02. Every item below is a round that was spent because the
item was skipped. Doing all six costs about ten minutes.

1. **Open every approved frame of this character, not one.** Front, back and side. Write down where each
   piece of GEAR is and what SHAPE it is in each. The back is the only view that showed the whole sword,
   and I drew the hilt twice without opening it.
2. **Lay the approved stand against this frame at offsets 0, +1 and -1.** A walk extreme can sit a row
   below the stand, and at offset 0 it looks like it shares nothing. `sprite_look.py --shift 0,1`.
3. **Find BOTH hands in the vanilla frame**, which are already bare skin, and name the row of each. The
   arm gets drawn toward the hand. Everything outboard of it is garment and gets cut.
4. **Name the band row and the waist row.** Band is the dark neck shadow, waist is the buckle. Nothing
   above the band can be arm. The jacket collar there is bulk in open air and it is cut, not recoloured.
5. **Decide which frames repeat and which do not**, and say so out loud. Repeats get his rows copied.
   Extremes get hand drawn. See "A rule draws the frames that REPEAT".
6. **Write down every design decision the frame needs**, take what earlier frames settled, and ask him
   the first one still open. One question.

### Compare at every plausible row shift before saying two frames share nothing

Source: 2026-11-02, twice in one session. I compared the four down walk frames to the stand row by row,
found no shared row in two of them, merged a bible row saying so, and drew those two from scratch. Their
whole torso sits ONE ROW LOWER. At +1 the jaw row differs by 2 px and the band row by 2 px, so his
answers for both rows transferred directly and I had thrown them away.

The belt is the cheapest alignment landmark: find the buckle row in each frame and subtract. Do that
before any row comparison, and state the offset in the finding.

### Once you know the offsets, CONVERT to body coordinates. Never compare screen coordinates across frames

Source: me, 2026-11-02, on the up walk. This is the worst mistake in this guide, because I made it
immediately after measuring the very numbers that prevent it.

I measured that `set:128` anim 1 dir 1 sits at a DIFFERENT offset per frame: frames 1 and 3 at -1, frames
0 and 2 at 0. I wrote that down. Then I built a table of which pixels to reveal by comparing screen `(x,y)`
across all five frames as though they shared one grid. They do not. A pixel at screen `(11,17)` is body
`(11,17)` in frames 0 and 2, and body `(11,18)` in frames 1 and 3.

The result: my table told an agent to paint strap `0x23` at `(11,17)` in the two frames where the owner's
own approved stand draws ARM `0x17` there. The agent caught it, shipped as instructed, and flagged it with
a comparison picture. Two pixels, but they sat on the arm's top edge where they read as an orange speck.

**The rule: the moment you have a per-frame offset, convert every coordinate to the STAND's body space and
do all reasoning there.** Carry the offset in the data, not in your head. A table of screen coordinates
spanning frames at different offsets is wrong in exactly the frames whose offset is not zero, which are
the frames you built the table to help.

The same mix-up also manufactures fake disagreements. I recorded that the frames "disagree" on the tone of
one pixel, `0x23` against `0x22`, and raised it as an open question for the owner. In body coordinates
there was no disagreement at all: the two values are two DIFFERENT body pixels, each consistent.

### Row equality is the wrong test for "can I lift this"

Same session, same cause: a test whose shape does not match the question.

I asked whether the up walk torsos repeat the stand, and tested whole-row equality. Zero rows matched, so I
wrote "every torso is hand drawn" into the brief and sent an agent off to draw four of them. Measured per
PIXEL instead, **94% of the jacket pixels in frames 1 and 3 sit exactly where the stand has jacket**: 56 of
59, and 55 of 58. They are repeat frames. One differing column, vanilla's own bare skin at x0 and x1,
breaks every row while leaving the whole garment region liftable.

**Test the region you actually intend to copy, not the row that contains it.** For an outfit swap that is
the garment mask. Row equality answers "is this row identical", which is a different and much rarer thing
than "did the owner already answer these pixels".

### Look at the source as a picture first

**Render the vanilla frame big, with numbered rows and columns, and look at it.** Then write down what each
row is: hair, eyes, jaw, neck, chest, belt, legs. Only then draw.

Reading the index grid instead is what caused the worst mistake of that session. In hex, row 15 is
`17 12 11 11 13 15 17`, which reads as "skin tones". In a picture it is obviously **his mouth**. Numbers do not
show anatomy. `scripts\permanent\rom\sprite_guard.py sheet` and the anatomy render both do.

### Render four views of your own work, and look at the WHOLE figure first

| Order | View | What it catches |
|---|---|---|
| 1 | **The whole figure, large, beside vanilla, head to foot** | anything outside the region you were working in |
| 2 | Game size, 1x | whether it survives at the size it is played at |
| 3 | A tight crop of the region you changed | everything the full figure hides |
| 4 | A changed-pixel map | that you strayed outside what you meant to touch |

**The order is the rule.** View 1 comes first and it is not optional. Views 3 and 4 are scoped to your own
edit, so they can only confirm what you already believe. A defect in a region you were not thinking about is
invisible to every one of them.

### Review the part of the frame you did NOT touch

On 2026-11-01 an outfit swap deleted half of Trunks' two pixel eye and turned the other half dark. He shipped
with one dark smear for a face. The owner found it. I had viewed the review sheets several times that session,
and the head was in them at 22x, next to the arms I was studying. I looked straight past it, because my
analysis said the subject was arms, so arms is what I saw.

Three habits caused it, and all three are easy to repeat:

- **I measured first and looked second.** A look that comes after a measurement only confirms the measurement.
  Look at the rendered frame and say what you see BEFORE running any check.
- **Every picture I built was cropped to my own edit.** Never crop the first review.
- **I verified my diff, not the character.** My invariant that pass was literally "nothing changed outside
  rows 16-25". A broken eye on row 13 passes that cleanly, because I did not break it on that pass.

### A metric that can reward damage is not a safety net

The standing rule "taking a garment off must shrink the silhouette" scored the deleted eye pixel as PROGRESS,
because deleting it shrank the silhouette.

Before trusting any check, ask what damage would SATISFY it. A pixel count cannot tell a filled sleeve from a
correct arm either: filling raises the count and losing the limb lowers it, so both land near a plausible
total. Checks of this kind are pointers. Only the eye decides.

### A palette index is a colour, never a role

`4F` and `51` are Trunks' jacket. They are ALSO his iris and its shadow, two rows higher. A mask told to
repaint every `4F` and `51` repaints his eye, and `--body-from 13` does not save it, because the eye IS on
rows 13 and 14.

Do not fix this with a row number per character. The garment is a **connected mass**; palette reuse on the
head is a small isolated island. Measured over 12 vanilla Trunks frames: every real garment component holds
27 px or more, and every eye is an isolated 2 px component sitting above the garment's top row. Separate them
by connectivity, protect the islands, and NAME what you protected.

### Let the guard find it, not the owner

```
py -3.14 -I scripts\permanent\rom\sprite_guard.py check <vanilla.png> <edited.png> --garment 51,50,4F,4E
```

It names every pixel an edit changed outside the garment. Run it before showing any outfit swap. On the real
frame it catches all 7 mouth pixels and all 3 chest pixels by coordinate, which is exactly what the owner had
to find by eye, twice.

A change outside the mask is not always wrong. A sloped shoulder is a deliberate one. The rule is that it must
be **declared with `--allow`**, not slipped in.

### Hand over the edit kit early

The owner drawing 11 pixels fixed in one pass what nine of my passes had not. Give him an editable base after
the **first** pass, not the ninth: the frame at 1x, the same at 12x, vanilla beside it, and a palette swatch of
the legal indices. `art\trunks_tank\edit-kit\` is the pattern.

### List the design decisions up front, then ask the first open one

Before drawing, write down every decision the frame needs: tank colour, strap colour, how much chest stays
bare, how wide the shoulders. Then take what earlier frames already settled, and **ask the owner the first one
that is still open**. One question, as always.

The list is the point. Each of those was a silent guess that cost him a message to veto, and the ones a
previous frame already answered should never be asked again.

### Read the whole reference folder

Not one image. A front render cannot tell you how a scabbard sits on the back.

## 4. Review rules

- **View every sheet yourself.** Tests and diff proofs do not check art. A green suite says nothing about whether
  a frame looks right.
- Render at **1x and 3x as well as large**. The game is played at 1x. A frame that works at 14x can fail at 1x.
- Put the new frame **beside the frame it replaces**, not alone.
- Fixes are made **by eye, frame by frame**. Rule passes over art are not allowed. Ask when unsure.

Source: the gi work. A rule pass is how a flat sash shipped for twelve days without anyone seeing it.

---

## 5. The promotion trap

Art that is reviewed is not art that ships. These are different folders.

| Folder | What it is |
|---|---|
| `art\<name>\` | What the build reads. Only this reaches a ROM |
| `art\base-audit\proposed\` | Frames drawn for review |
| `art\base-audit\approved\` | Frames signed off |

On 2026-10-31 we found `art\gi_base\` was last written 2026-10-19, while 150 reviewed frames were dated
2026-10-24 and 25. **None had ever gone back in.** The dev ROM shipped stale art for twelve days, and every
review in between looked at frames the game never used.

**The check:** a thing is only in the build when it has been **read back out of a built ROM**. Not when the PNG
is saved. Not when the test passes.

`scripts\one-time\2026-10-31-gi-v2\sweep_art_against_build.py` sweeps every per-frame PNG under `art\` against
the art in a built ROM and names the ones that do not match.

---

## 6. Clean room

- Buu's Fury art is official and may be ported.
- Never copy another modder's art.
- The Z Hack is inspiration only. Study it into **written rules**, then draw from our own sources with their
  sheets closed. Never trace. Nothing from `zhack\` goes into `art\`, a module or a build.
- Keep the script trail. A scripted path from a vanilla frame plus the edit log is what proves a frame is ours.

**Note:** an outfit swap built from a vanilla frame will resemble anyone else's swap of the same frame, because
both start from the same pixels. The trail is the proof, not the difference.

---

## 7. Tools

```
rem Any number of frames side by side, big, with the palette index in every cell.
rem --shift i,dy aligns a stand against a walk extreme that sits a row lower.
rem --plain drops the numbers so SHAPE reads. --palette forces the live palette on every frame,
rem because a set's own embedded palette is often not the one the game draws it with.
py -3.14 -I scripts\permanent\rom\sprite_look.py <out.png> <frame.png> [<frame.png>...] ^
    [--rows 12-26] [--zoom 34] [--plain] [--small] [--palette <png>] [--shift 0,1]

rem Hold an outfit swap to the garment. Names every vanilla pixel the edit overwrote
py -3.14 -I scripts\permanent\rom\sprite_guard.py check <vanilla.png> <edited.png> --garment 51,50,4F,4E

rem Vanilla, edited, and a map of every changed pixel, plus 3x and game size
py -3.14 -I scripts\permanent\rom\sprite_guard.py sheet <vanilla.png> <edited.png> <out.png> [--crop 11-25]

rem Draw what a built ROM really holds, one row per (set, anim, dir)
py -3.14 -P scripts\permanent\rom\rom_sheet.py <rom.gba> <set>[,<set>...] <out.png> [--anims 0,1] [--dirs 0,2]

rem Write every record of a set as its own PNG at 1x and 3x
py -3.14 -P scripts\permanent\rom\rom_sheet.py <rom.gba> <set> --frames <out_dir>

rem Check that the art folders match a built ROM
py -3.14 -P scripts\one-time\2026-10-31-gi-v2\sweep_art_against_build.py
```
