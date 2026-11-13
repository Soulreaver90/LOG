# The Goku chamber-exit form loss: cause and fix

## Symptom

The owner reports Goku loses his Super Saiyan form at the Time Chamber.

## The scene

`rom:0x3DE620` (table word `rom:0x3DE774`), the Vegeta and Trunks chamber exit, map 9,3 region 2,
gated on flag 148 set and flag 149 clear. Bible B0644.

## The rule it breaks

Bible B0554: `appearance_revert` `@0x08003ED4` **skips only the current leader**. `ext 70` runs
`set_leader` first, so the new leader is the one record the revert leaves alone. Every other
transformed record goes back to its `+5` entry. B0469: ext 70 reverts Goku 20 to 19.

## Measured order inside the record

| Record offset | Operation | Source |
|---|---|---|
| 0x7C | `set_flag(149)` | vanilla |
| **0x7C+4** | **`appearance(4, 61)`, Goku to entry 20** | **fullpower_ssj, WRONG PLACE** |
| 0x90 | `leader(2)`, the lead goes to Vegeta | vanilla |
| 0x94 | `appearance(3, 129)` | vanilla |
| 0x9B | `appearance(2, 138)` | vanilla |

Offsets measured with `scene_lib` against the base ROM, not read off a label.

Goku is character 4. The new leader is character 2. They differ, so the revert undoes Goku's
entry 20 immediately after it is set. Vanilla's own two appearance calls sit AFTER the leader
change, which is why they survive. Ours is the only one before it.

## The fix

Move the insert from the `set_flag(149)` anchor to the `leader(2)` anchor, so Goku's appearance
is set after the revert has run, beside vanilla's two.

In `scripts\permanent\patches\fullpower_ssj.py`, `RECORDS["door_seq33"]`:

    from:  0x7C, "0095021b", "0095021b" "0004003d0249"
    to:    0x90, "00020246", "00020246" "0004003d0249"

`00020246` is `leader(2)`, confirmed present at record offset 0x90. The entry carries both an
offset and the expected old bytes, so the patch fails closed if either moves.

## What this does NOT prove

The static evidence is strong and three sources agree: the lint rule in `test_battle_start`,
bible rows B0554 and B0644, and the patch source. It is still not a play-test. The owner must
confirm in mGBA that Goku is Super Saiyan after the scene.

## Test save

No existing save can reach this scene. All 192 save files in `builds\` carry flag 149 already
set, so the scene has played in every one. A new save is built with flag 149 cleared and flag 148
left set, which makes the scene replay on entering map 9,3. The flag reader was validated first
against three answers the suite already pins in `log2_poc_r31_chamber2.sav`.
