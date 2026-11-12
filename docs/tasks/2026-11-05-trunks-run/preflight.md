# Pre-flight: Trunks tank top, the DOWN run (anim 13, dir 0)

Done before drawing a pixel, following `docs\sprite-guide.md` section 3. Owner picked down, then up,
with the side left until the tooling is widened.

## The frames

| Set | Dir | Frames | Headers |
|---|---|---|---|
| 128 base | 0 down | 4 | `0x357690`, `0x357784`, `0x35788C`, `0x35797C` |
| 128 base | 1 up | 4 | `0x357A7C`, `0x357B7C`, `0x357C8C`, `0x357D94` |
| 134 ssj | 0 down | 4 | `0x37B700`, `0x37B7F8`, `0x37B904`, `0x37B9F0` |
| 134 ssj | 1 up | 4 | `0x37BAF0`, `0x37BBFC`, `0x37BD10`, `0x37BE24` |

All eight headers per set are distinct: no reuse between down and up. All are 16x32, dx 0.

> [!IMPORTANT]
> The SIDE run (dirs 2 and 3) is **32x32 with dx -8**, and dir 3 reuses dir 2's headers. Our pipeline
> assumes 16 wide throughout, so side needs tooling work first. Deferred by the owner.

## 1. Gear: there is none to track

| Frame | jacket | baldric | scabbard | sword | bare skin |
|---|---|---|---|---|---|
| vanilla walk 0 | 46 | 5 | 10 | 1 | 58 |
| vanilla run 0 | 48 | 0 | 0 | 0 | 47 |
| vanilla run 1 | 46 | 1 | 0 | 0 | 53 |
| vanilla run 2 | 42 | 0 | 0 | 0 | 48 |
| vanilla run 3 | 34 | 2 | 0 | 0 | 55 |

**The down run shows no sword, no scabbard and no baldric.** Running toward the camera puts the sword
behind him. Only the jacket comes off, which makes this simpler than the walk.

Trap avoided: the `0x22` pixels at rows 27 to 30 are BOOTS, not scabbard. `0x22` is a colour used by
both. See the guide, "A palette index is a colour, never a role".

## 2. Alignment: the run is NOT a shifted walk

| | walk and idle | down run |
|---|---|---|
| boot rows | 21 to 30 | **27 to 30** |
| top of figure | row 2 to 3 | row 3 to 5 |

Both stand on the same floor, but the run's visible leg is four rows shorter. It is a compressed,
crouched pose, not the walk moved up or down. No row transfers wholesale.

Trap avoided: my first pass read `0x02` white as the belt buckle and concluded the torso sat 4 to 6 rows
HIGHER. Those are the eyes. The boot row is the reliable landmark here, because the belt is hidden in
every down run frame.

## 3. Which frames repeat

Pixels differing, out of 512:

| Pair | Direct | Mirrored | Best shift |
|---|---|---|---|
| run 0 vs run 2 | **98** | 167 | 98 at dy 0 |
| run 1 vs run 3 | **118** | 194 | 118 at dy 0 |
| any cross pair | 267 to 277 | worse | 172 to 196 |

**No frame is a mirror of another, and no pair is close enough to copy.** The two passing frames (0 and
2) are the closest pair, then the two extremes (1 and 3). So this is four hand drawn frames, with work
on 0 transferring partly to 2 and 1 to 3. The guide's rule applies: a rule draws the frames that repeat,
and these do not repeat.

## 4. What earlier frames already settled

Taken, not re-asked:

- Tank top shape and colours, from the approved front walk.
- The bare arm ramp, `17` outer, `13` mid, `11` inner, three pixels wide.
- The collar fill role map `E5->14`, `64->2E`, `62->78`, owner 2026-11-05. Applies to the Super Saiyan
  derivation, not to the base art.
- Legs, boots and the one body rule are unchanged.

## 5. Open decision

Process, not art: whether to draw one frame for approval before committing to the other three. Asked.
