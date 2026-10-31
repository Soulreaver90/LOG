# Why our gi reads worse than vanilla, and what the other hacks really did

Date: 2026-10-31. Scripts: `scripts\one-time\2026-10-31-sprite-diagnosis\`.
Pictures in this folder: `front-vs-back.png`, `back-view-three-way.png`.

Measured on the current dev art. Set 157 was exported from `builds\log2_poc_r40.gba`
(SHA-1 `14d6b831`) and is byte-identical to the older `ingame_r28` export, so the
numbers below describe what is in the game now.

> [!NOTE]
> Set 157 is a clone of vanilla `set:56`. Both have the same 162 records and the
> same frame shapes. Only the colours differ, so every comparison here is controlled.

---

## 1. The defect: our base gi goes dark from behind

Bright means a pixel at 60 % value or more, background excluded.

| Set | dir 0 | dir 1 (back) | dir 2 | dir 3 |
|---|---|---|---|---|
| Vanilla `set:56` median bright | 13.7 % | 7.1 % | 10.9 % | 10.2 % |
| Vanilla records under 2 % bright | 0 | **0** | 0 | 0 |
| Ours `set:157` median bright | 8.8 % | 2.1 % | 5.0 % | 4.8 % |
| Ours records under 2 % bright | 0 | **33** | 0 | 4 |

Vanilla never lets a record fall under 2 % bright, in any direction. Ours does it
33 times, and all but 4 are the back view. The worst reach 0.6 %.

The asymmetry survives a lower cutoff. At 140 instead of 153, dir 1 still has 10
records under 2 % while dir 0 and dir 2 have none.

`set:158` (Super Saiyan gi) does not have the problem: 34.1 % bright, 0 records
under 2 %. The yellow hair supplies the light.

**Cause.** Vanilla Gohan wears Saiyan armor with white gloves, white boots and a
yellow collar. Those sit at the ends of the limbs, so they stay visible from every
angle. Our gi replaced the gloves with bare hands and the boots with dark brown.
From the front the face and forearms still supply light. From the back there is no
face, so nothing is left.

---

## 2. The Z Hack did not solve this either

This corrects the first draft of this report, which claimed the other hacks only
redrew Super Saiyan sets. They did not. The Z Hack redrew 21 sets, `set:56` among
them, which is black-haired Gohan in the same purple gi.

Their back view, measured off `zhack\sprites\set56_redrawn.png`, against the EU
vanilla row on the same sheet:

| `set:56` dir 1 | bright >= 153 | bright >= 140 |
|---|---|---|
| EU vanilla | 6.2 % | 11.0 % |
| Z Hack gi | **1.8 %** | 4.7 % |

They drop it by the same factor we do, about 3.4x. Their black-haired gi back view
is just as dark as ours.

So the honest answer to "why did theirs succeed" is that on this particular problem
it did not. What differs is which sprites get shown. Both hacks put their visible
work on the Super Saiyan sets, where a large yellow hair mass lights the figure from
all four sides.

Two smaller things they do better in that same frame, visible in `back-view-three-way.png`:

- Their sash is a continuous bright blue band across the full width. Ours is a dark
  red band, broken in the middle, and from behind it is the only feature in the frame.
- Their boots are a mid brown with a lighter top edge. Ours are dark brown and merge
  into the shadow ellipse.

---

## 3. Claims I checked and had to drop

Recorded so nobody re-derives them.

- **"Ours uses too many colours."** False. 23 in the body against vanilla's 22.
- **"Ours is too dark overall."** False. The Z Hack gi body is darker than ours,
  median value 54 against our 64, with no pixel over 60 % value at all.
- **"Ours lost an outline vanilla had."** False. Vanilla `set:56` has no dark
  outline on the body either.
- **"Our silhouette edge is unlit."** Overstated. One frame gives 0 % against
  vanilla's 21 %, but across all 288 records the gap only opens at one cutoff:

  | Edge pixels at or over | vanilla | ours |
  |---|---|---|
  | 60 | 34.9 % | 30.9 % |
  | 70 | 34.0 % | 24.8 % |
  | 90 | 28.9 % | 5.0 % |
  | 120 | 6.2 % | 4.6 % |
  | 153 | 3.9 % | 3.2 % |

  The real effect is modest: our rim sits about one palette step darker than
  vanilla's, in the 70 to 90 band rather than 90 to 120.

- **Buu's Fury as proof.** BF Gohan's strips never fall under 2 % bright, but he is
  in a white shirt there, not a gi. The white comes with the outfit. BF Goku, who
  does wear a gi, breaks the rule in 9 cells. So this is not a law of the engine.

---

## 4. What to change

1. Put light back at the ends of the limbs. The boots are the cheapest fix: a tan
   or orange highlight row on the boot top, as vanilla does with white.
2. Lighten the sash or widen it, and make it continuous. From behind it currently
   defines the character.
3. Give the gi one light direction. Ours puts dark navy inside the purple as
   speckle with no consistent side.
4. Set a gate: no record under 2 % bright, in any direction. Vanilla passes this
   on all 162. Ours fails 33.

## 5. The process lesson, which is the bigger one

Every review sheet I have built leads with dir 0. I approved the gi frame
by frame from the front. The back view was never put in front of anyone, so a
defect in a quarter of the art went 12 builds without being seen.

Make a per-direction check part of every sprite review: show dir 1 beside dir 0, and
print the bright fraction per direction before asking for approval.
