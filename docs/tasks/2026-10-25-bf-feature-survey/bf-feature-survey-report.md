# Buu's Fury features worth porting: survey report

This report lists the Buu's Fury (BF) features that LoG II lacks, ranks them, and gives a trial module design for the top picks. It is a study only: no patch, no build list change, no ROM written.

Labels: **C** = CONFIRMED (address and listing or bytes), **L** = LIKELY, **S** = SPECULATIVE. All files named below are in `scripts\one-time\2026-10-25-bf-feature-survey\` unless a path says otherwise.

---

## SHIPPED and PENDING

These tables show what this task delivered and what still waits on me.

| SHIPPED (your ask) | Where |
|---|---|
| "Any other features you think we should port over?" | "Feature map" (every area of BF, with addresses) and "Ranked candidates" (16 rows) |
| "Maybe more of the GUI?" | Feature map rows for menus; I pick 2 (STAT badge), 4 (chapter cards), rank 6 (BF status look); emulator step 2 (BF menu screenshots) |
| "The stat system?" | "How BF stats work" and pick 1 (`stat_points`); 3 points per level confirmed |
| "etc" | Picks 3 (low-HP beep) and 5 (named supplies); moves, equipment and shops ranked |
| Trial module designs for 5 top picks (none built) | "Top picks" |
| 25 bible rows tagged BFP | `bible_rows.md` |
| Renders: BF STAT badge (BF colours and LoG II palette preview), BF menu frames, BF full screens | `stat_badge_*.png`, `bf_menu_*_objpal.png`, `bf_screens_sheet.png` |
| Dumps: all 1,534 BF UI strings, the code site of each string, the LoG II UI strings | `bf_strings.txt`, `bf_strrefs.txt`, `log2_ui_strings.txt` |

| PENDING (mine) | Why |
|---|---|
| Pick the trial modules to build | Nothing is built until you say which |
| Decide the stat point store | The only free place is save padding, and `global.md` says "no new save fields" |
| Decide points per level | BF gives 3; LoG II's random gains average 3.7-4.6 |
| Run the emulator steps | BF menu screenshots, start level, badge place and beep sound need a real run |
| Write chapter names (if you want chapter cards) | Text is yours |

> [!IMPORTANT]
> Design 6.3 asked to "confirm in the ROM" that BF gives 3 points per level. **Confirmed:** level-up `0x08013678` adds 3 x (levels gained) to record +0x2C (`0x08013742` `sub r0,r7,r6 ; lsl r3,r0,#1 ; add r0,r3,r0` ... `0x08013752` `strh r0,[r4,#0x2c]`). One point gives +1 to one stat, and a stat can never pass the character's level.

---

## How BF stats work

This section explains the BF stat system, because it is the core of my ask and of slice 2.

| Part | BF | LoG II | Label |
|---|---|---|---|
| Stats | STR, POW, END, SPD: u8 base at record +0x28..+0x2B, u16 live values at +0x4C, +0x4E, +0x50, +0x54 (+0x52 = hidden ki END) | STR, POW, END: 8.8 at record +0xA/+0xC/+0xE, cap 100 | C |
| Level-up | Raises max HP and max ki only (growth table `0x086B72E0`), plus 3 points | Random STR/POW/END gains from range table `rom:0x1D95F0`, cap 100 (`@0x08003C6E`) | C |
| Spend | Status page mode: Right +1 if points > 0 and stat < level; Left takes back; confirm saves (`0x080157A4`, `0x080156F2`) | None | C |
| Who can be raised | STR, POW, END only (SPD comes from gear) | n/a | C |
| Live stats | Rebuilt from base + 4 gear slots + a timed buff (`0x08013C66`) | Base + form bonus (form apply) | C |
| Status colours | Live value green above base, red below, plain when equal | Gold bar segment for the form bonus (our r9 patch) | C |
| Reminder | "STAT" badge on the HUD while points are unspent (`0x0800BCC8`) | None | C |
| Level range | 50-200 (EXP table `0x086B7088`, 150 entries) | 1-50 | L (start level needs a run) |
| Damage | u16 stats, END soft cap at 200 (to 220), term 221 - END | u8 stats, term 0x80 - END | C |

**Balance numbers for points per level** (LoG II range table, mean gain per level, sum of three stats):

| Gohan | Piccolo | Vegeta | Trunks | Goku | Hercule |
|---|---|---|---|---|---|
| 4.59 | 3.82 | 3.90 | 3.68 | 3.94 | 1.50 |

- 3 points per level gives 65-82 % of the vanilla gain for the five fighters.
- 4 points per level gives 87-109 %.
- The BF rule "stat below level" does not fit LoG II: LoG II stats reach about 100 at level 50. Keep the LoG II cap of 100. Do not copy the BF END cap: LoG II damage uses `0x80 - END`, so END must stay at 127 or below (bible FRM, T6 rows).

---

## Feature map

Each row gives how BF does it, the LoG II counterpart and the gap. "Port?" says whether the row became a candidate.

| Area | BF (code and data) | LoG II counterpart | Gap | Label | Port? |
|---|---|---|---|---|---|
| Pause menu | Tab buttons from `0x080147B8` (`0x08013E64`, ids 0-7). Strings: Status, Skills, Journal, Inventory, Equip, Options, Pause | Character menu `@0x08003480`: status, hold special, 2 ability pages; Items, Journal, Save, Sleep, Switch | Look only; tab order not traced | C (strings, builder), L (order) | Look: after screenshots |
| Status page | `0x0801514A`: name and LVL, HP, EP, XP, NXT LVL, Zenie, Time, 4 stats coloured, Pts. | `@0x0800379C` (our status_bonus copy): level, HP/EP bars, stat bars x/100 with gold bonus, EXP, NEXT | Points, colours, Time, Zenie | C | Yes (pick 1) |
| Level-up and points | 3 points per level `0x08013742`; spend rule `0x08015862` | Random gains `@0x08003CA0`, text `rom:0x3B64E8` | Whole system | C | Yes (pick 1) |
| STAT badge | HUD object, 4 frames 16x16 at `0x087144D8`, while points > 0 | None | Badge | C | Yes (pick 2) |
| Equipment | Table `0x086F82EC`, 162 x 44 B, 4 slots, required level, stat and XP bonus, effect scripts; equip page `0x08016E4A` | None (OVW: no equipment) | Whole system | C | No: design 3 non-goal for the LoG II half; keep for the Buu saga |
| Supplies | Foods (HP 20-1500), drinks (EP 20-2500), Senzu, Holy Water (30 s buff, `0x080046AE`), Use and Drop | Senzu, stat capsules; items 11-16 have HP/EP handlers but debug names and no pickups | Named healing items | C (handlers, pickups), L (unused) | Yes (pick 5) |
| Money and shops | Zenie (record base +0x4F4), Buy x N, Sell x N, Z-Mart | None | Whole system | C (strings, status field) | No: big; Buu saga |
| Map and fast travel | 452 maps; fly control text "A Button: Descend/Land B Button: Ascend" (string 597) | World map by the Golden Capsule; R screen | Altitude flight | L | No |
| Save | "Save Game", "Saving..." (`0x080394E8`, called through a vtable) | "Save" in the pause list; save points on maps | Not known if BF saves anywhere | S | Emulator step 4 |
| Character switch | "Switch Character" (string 12) | Switch Characters `@0x08011172` | None found | L | No |
| Forms | Z and Z3 abilities, per-character ki pools, cooldown on each record +4 (HKS rows) | Party-wide cooldown (FCD rows); pool ported in r39 | Per-character cooldown (known from FCD) | C | Known, not re-proposed |
| Ki moves | 24 abilities with name and help text (`rom:0x71DAF8`): Final Flash, Instant Transmission, Masenkoha (cursor), Dragon Fist, Energy Sword and others | 14 abilities `rom:0x1D9900`, help text in UI strings | Moves with a cursor; Final Flash; Instant Transmission | C (table) | Later (rank 7-9) |
| Block | R hold, ki shield (BLK rows) | None | On hold (mine) | C | Known only |
| Beam struggle | BMS study | In work | n/a | C | Known only |
| Dialogue and text | UTF-16 UI strings with colour codes `{0008}{n}`; BF dialog encoding still open (CFS row) | ASCII, `@`, `#`, `^` controls | Inline colour words | C (UI), S (dialog) | No |
| Quest log | Journal: Goals, Completed Goals; 40 goal strings 614-653 | Journal: 43 entries, 29 story goals (`rom:0x6D68DC`) | None | C | No |
| Scouter | "Capsule Corporation database": bios for friends and enemies (strings 986-1311); "No Portrait Data", "Database Empty" | Scan and database, 128 entries (R31-R35 rows), same two strings | None found | C (strings) | No |
| Chapter cards | Scene `0x0803369E`: two lines on a clear screen, 128 frames or A/B; 12 chapters | None | Whole feature | C | Yes (pick 4) |
| Low-HP beep | HUD `0x0800BA34`-`0x0800BA6A`: HP x 5 <= max, every 60 frames | None in the HUD routines | Beep | C (BF), L (LoG II none) | Yes (pick 3) |
| Play time | Status "TIME h:mm" from the frame counter | None | Needs a save field | C | No |
| Rank titles | 50 titles "Monkey" .. "Eternal Dragon" (strings 1474-1523) | None | User not traced | S | No |
| Options | Language, SFX and music volume, text speed, sleep, credits | Same list | None | C | No |

---

## Ranked candidates

The table ranks every candidate. Value is for the player; effort counts new code, data and art; risk is to old saves and to the r39 modules.

| Rank | Candidate | Value | Effort | Risk to saves and modules | VRAM | I draw |
|---|---|---|---|---|---|---|
| **1** | **Stat points (BF rule, LoG II caps)** | High: slice 2, design 6.3 | About 0x300-0x400 B code (S), 1-6 B data, one text edit | Needs 6 padding bytes (final decisions). Old saves load with 0 points. Builds on the status_bonus page copy | None (BG canvas already used) | Nothing |
| **2** | **STAT badge on the HUD** | Medium: reminder | About 0x100 B code, 0x400 B art | Chains after bf_ki_pool's `hud_draw`. Needs pick 1 | OBJ 0x100 B from the HUD allocator `0x080067AC` (free space L) | One shade (see list), the place on screen |
| **3** | **Low-HP warning beep** | Medium: QoL in fights | About 0x60 B code, 12 B entry, 1,298 B sample | Chains after `hud_draw`; 4 B of free IWRAM | None | Nothing (listen and pick a sound) |
| **4** | **Chapter title cards** | Low-medium: story flavour | About 0x200 B code, text | New scene on the Continue path (L) | BG canvas while shown | Nothing; chapter names |
| **5** | **Named supplies (items 11-16)** | Medium-low | Data: 6 names, 6 texts, pickups | Pickup lists move (map table rows) | None | 6 item icons, or approve BF icon ports |
| 6 | BF status page look | Medium (backlog idea 6.7) | High: page rewrite | Status page copy | BG only | Possibly a frame |
| 7 | Instant Transmission (Goku) | High fun, canon in the Cell saga | High: cursor, target search, teleport and return | Ability table growth (14 entries now) | Cursor OBJ | Vanish frames, HUD icon |
| 8 | Final Flash (Vegeta) | Medium, canon in the Cell saga | Medium-high: beam code reuse | Ability table growth | Beam effect reuse (L) | Pose frames, HUD icon |
| 9 | Masenkoha with a cursor (Gohan) | Low-medium | Medium | Ability change | Cursor OBJ | HUD icon |
| 10 | Per-character transform cooldown | Medium (FCD study) | Medium | Save field per record | None | Nothing |
| 11 | Holy Water timed buff | Low | Small code after pick 5 | Item table | None | Icon |
| 12 | Equipment | High in the Buu saga | Very high | New save fields | Menu icons | 162 icons exist in BF |
| 13 | Zenie and shops | Medium in the Buu saga | Very high | New save fields | Menu | Shop art |
| 14 | SPD stat | Low | Medium | New save field | None | Nothing |
| 15 | Play time on status | Low | Small | New save field | None | Nothing |
| 16 | Rank titles | Low | Unknown | Unknown | None | Nothing |

---

## Top picks: trial module designs

Each pick is a trial patch module with its own build list (the main `build_list.txt` lines plus the trial line). Do not touch `build_list_trial.txt` or the Vegeta list. Nothing below is built.

### Pick 1: `stat_points`

The level-up gives points instead of random stats, and the status page spends them.

- **Files:** `scripts\permanent\patches\stat_points.py`, `scripts\permanent\build_list_trial_statpts.txt`, ROM in `builds\mockups\2026-10-25-stat-points\`.
- **Data:** a 6-byte table, points per level per character (default 3 for each fighter; I may pick 4, and 1 or 2 for Hercule). Stat cap stays 100.
- **Store (final decisions):** one byte per character in save padding: struct +0x05, +0x06, +0x07 (characters 0-2) and +0x15D, +0x15E, +0x15F (3-5). They read 0 in all 89 build states, and the slot copy (0x164 bytes) keeps them. Old saves start with 0 points.
- **Level-up:** redirect the gain helper `@0x08003C6E` with an 8-byte `ldr r3,=new ; bx r3` (the fullpower_ssj pattern). Its 3 callers are all in level-up `@0x08003CA0` (C). The new body adds points x levels for the STR call and returns at once for POW and END. Story level-ups (ext 98, the chamber +1) give points too.
- **Level-up text:** `rom:0x3B64E8` "Attribute Bonus / Strength: +%d / Power: +%d / Endurance: +%d" becomes "Stat Points: +%d". The three values come from script ext ops 131, 132, 133 (words `rom:0x3B5F34`-`rom:0x3B5F3C`), which push the bytes at `0x03001FC1`-`0x03001FC3` (C). Level-up overwrites those bytes after the helper runs (`@0x08003D38`), so the helper cannot write the value there. Instead, the new helper writes the gained points to its own RAM byte, and the ext 131 word is repointed to a handler that pushes that byte (a table word is a safe hook, FCD row). Check that the script consumes the first push for the first `%d` (L).
- **Input:** repoint char menu vtable `0x080248CC` +0x68 (now `0x08003B73`, `mov r0,#0 ; bx lr`) to `page_input`. On page 0: A enters spend mode when points > 0. In the mode: Up/Down pick STR, POW or END; Right +1 (points left, stat < 100); Left -1 (not below the value at entry); A saves; B cancels. Return 1 for each key used, so page change keeps working outside the mode.
- **Draw:** in the status_bonus page copy, print "Pts. N"; in the mode, mark the picked row and show raised values in green (BF rule).
- **After save:** if the character is the leader, call `form_reapply` through `find_player` (status_bonus pattern), then redraw page 0.
- **Tests:** level 40 to 41 adds the table value to the right byte for each character; stats do not change; spend stops at 100; refund stops at the entry value; vtable word; old save gives 0 points.
- **my checks:** level up in a fight, read the text, open status, spend 3 points, see bars and numbers, transform and see the gold segment still right.

### Pick 2: `stat_badge`

A small "STAT" badge shows on the HUD while the leader has unspent points.

- **Files:** `stat_badge.py`, `build_list_trial_statbadge.txt` (main list + `stat_points` + `stat_badge`).
- **Hook:** wrap the current HUD vtable `0x0802408C` +0x10 word (bf_ki_pool's `hud_draw`), the way bf_ki_pool checks the word it replaces.
- **Behaviour:** after the HUD draw, if the leader's points > 0, allocate 0x100 B OBJ VRAM once with `0x080067AC(manager [0x083B5348 +8], 0x100)` (the HUD's own call shape, C), copy the frame (tick >> 3) & 3, add one 16x16 8bpp OAM entry. Free it at 0 points (the free routine is not traced: L).
- **Art:** the BF 4 frames (`0x087144D8`, 0x400 B) remapped to the LoG II OBJ palette: 1 > 1, 5 > 8, 30 > 43, 109 > 39, 110 > 8 (distance 40, so two yellows merge). See `stat_badge_bf_x8.png` and `stat_badge_log2map_x8.png`.
- **RAM:** a home in free IWRAM for the badge's tile index, frame counter and an "allocated" tag. This RAM is above the crt0 zero fill (HKS row), so it holds junk at boot: use a tag word that the code writes on first use and checks on every frame, as bf_ki_pool does with its +2 tag.
- **Tests:** draw with points 0 and 3, OAM word, VRAM write size, chain to the old `hud_draw`, junk RAM at start.
- **Risk:** OAM and VRAM space at run time (L). Check in mGBA's OBJ viewer.

### Pick 3: `low_hp_beep`

The HUD beeps every second while the leader's HP is at 20 % or less, as in BF.

- **Files:** `low_hp_beep.py`, `build_list_trial_lowhp.txt`.
- **Hook:** wrap the current `hud_draw` word, as in pick 2 (if both are built, chain one after the other).
- **Rule (BF `0x0800BA34`-`0x0800BA6A`):** HP not 0, HP x 5 <= max HP, and more than 60 frames since the last beep (VBlank counter `0x03000E20`). Skip while a scene runs (`[0x03001FDC] != 0`, r27 marker) so text boxes stay quiet.
- **Sound:** `sound_start(r0 = [0x083B534C] + 0x5C4, r1 = entry, r2 = 0x20, r3 = 0)`, the LoG II call shape at `@0x08008BB2`-`@0x08008BC4` (C). Entry: a new 12-byte record in the expansion area pointing at a copy of the BF sample (`0x082FD53D`, 1,298 samples, rate 0x1F40), or a LoG II sound I pick. No table growth is needed.
- **RAM:** a 4-byte stamp in free IWRAM, for example `0x03003A10` (bf_ki_pool uses `0x03003A00`-`0x03003A0D`); the module test must check every patch's RAM list. This RAM is not zeroed at boot (HKS row). BF tests the gap with a signed compare (`sub r1,r0,r1 ; cmp r1,#0x3c ; ble`), so a junk stamp could mute the beep for a long time. Use an unsigned compare of (counter - stamp), or reset the stamp when the gap is out of range.
- **Tests:** HP 19/100 beeps, 21/100 does not, HP 0 does not, 60-frame spacing, scene flag mutes, junk stamp at start.

### Pick 4: `chapter_cards`

A short title card ("Chapter 3 / The Androids") shows at chosen story points, like BF's 12 chapter cards.

- **Files:** `chapter_cards.py`, `build_list_trial_chapters.txt`.
- **BF model:** scene `0x0803369E` clears the screen, draws two centred lines, waits 0x80 frames or A/B (`0x0803377C`). Port the idea, not the code (the menus and player do not share code, DIS row).
- **LoG II build:** push a new scene (`scene_push` `@0x0801F2F4`). Enter: the character menu's BG setup (`@0x08000B3C`: BG3, menu palette `rom:0x1D4F50`), a canvas (`@0x08020E5C`), two lines with `text_draw` `@0x0801F636` (menu font), copy to BG VRAM. Tick: 128 frames or A/B.
- **Trial trigger:** Continue from file select (`@0x08001848`) shows the card for the current chapter, picked from a story-flag table (for example `flag:158` Dragon Ball quest, `flag:193` Cell Games). This lets me judge the look with any save. Story-point triggers come after approval.
- **My input:** chapter names and the flag for each.
- **Risk:** the scene push on the Continue path (L); BG state on return (L).

### Pick 5: `named_supplies`

LoG II already has six unused healing items with working effects; give them real names and put them in the world.

- **Facts:** items 11-16 use the HP and EP handlers (`0x0800F593`, `0x0800F639`; item 11 +10 %, item 12 +20 % of max HP), carry debug names ("HealthBonusSmall"), and are in no map pickup list (C, all 327 maps).
- **Files:** `named_supplies.py`, `build_list_trial_supplies.txt`.
- **Change:** point UI string table entries 78-89 (`@0x080E2840` + 4 x id) at new names and texts in the expansion area, for example Rice Ball, Chicken Leg, Hamburger, Milk, Soda, Root Beer (BF names). Add pickups on a few maps (map +6 count and +0x1C list must move: map table rows at `rom:0x409368`).
- **Open:** the item icons (+8 world, +0x18 menu) may be placeholders (not checked). The handler percentages for items 13-16 are not read.

---

## My drawing list

These are the art items the top picks need from me.

| Pick | Item | Size | Note |
|---|---|---|---|
| 2 | STAT badge shade fix | 16x16, 4 frames | BF index 110 maps to LoG II 8 at distance 40; pick another yellow or redraw the light row |
| 2 | Badge place | n/a | BF draws it at x 92 (y not traced); the LoG II HUD layout differs |
| 5 | 6 item icons, if the vanilla ones are placeholders | Menu and world icon sizes of the item table | Or approve ports of the BF food icons |
| 7, 8 | Instant Transmission and Final Flash poses, HUD icons 32x16 | Later | Only if these picks are chosen |

Picks 1, 3 and 4 need no art.

---

## Emulator steps for me

These facts need a real run. Work on copies, never on files in `data\`.

1. **Copy:** copy `data\roms\Dragon Ball Z - Buu's Fury (USA).gba` and its `.sav` into a new folder `scratch\bf-shots\`. Open the copy in mGBA 0.10.5. mGBA writes the `.sav` next to the ROM it opened, so the copy protects `data\`.
2. **Menu screenshots:** load a save, press Start, and take a screenshot (F12) of each tab: Status, Status in point-spend mode (if a character has points), Skills, Journal (Goals and Completed Goals), Inventory (Supplies and Story Items), Equip (slot list and item list), Options. Put the PNG files in `scratch\bf-shots\`. Expected: one PNG per tab. These decide pick 6.
3. **Start level:** on a new game, open Status and note Goku's "LVL". Expected: 50 if the EXP-table reading is right.
4. **Save anywhere:** in BF, open the pause menu away from any save point. Note if "Save Game" is there and works. Do the same in vanilla LoG II with "Save". Expected: yes or no for each game.
5. **Badge and beep:** level up once without spending points. Note where the STAT badge shows on screen. Then let HP drop below one fifth and listen. Expected: the badge near the HUD, and a short beep once a second.

---

## What I verified and what I assume

This section separates checked facts from assumptions.

- **Verified:** every C row in `bible_rows.md` by listing or bytes; the STAT badge render decodes (4 clean frames); the 89 states decode (map 14,1,1 and cooldown 0x461 on `log2_poc_r39_celljr.ss2` match the FCD row); the vtable +0x68 word and the level-up text are the same in r39 as in the base ROM.
- **Assumed:** the BF level range starts at 50 (L); the menu frame `rom:0x7319E0` is the scouter or database screen (L); no LoG II code writes the padding bytes (three shapes in RSS plus 89 states, not a full proof).
- **Not done:** the BF dialog encoding, the BF pause tab order, the item icon state of LoG II items 11-16, and who triggers the BF chapter card.

## Files

The study scripts and their outputs.

| File | What |
|---|---|
| `bf_strings.py`, `bf_strings.txt` | All 1,534 BF UI strings |
| `bf_strrefs.py`, `bf_strrefs.txt` | Code sites that load each string (constant tracker) |
| `log2_ui_strings.py`, `log2_ui_strings.txt` | The 260 LoG II UI strings |
| `bfq.py`, `bf_grep.py` | Read-only probe helpers |
| `padding_states.py`, `padding_states.txt` | Save padding bytes in 89 states |
| `render_bf_screens.py`, `bf_screens_sheet.png`, `bf_screen_*.png` | The 8 full-screen BF frames (menu frames in the OBJ palette) |
| `bf_menu_*_objpal.png` | The 3 menu frames at 2x in the OBJ palette |
| `render_stat_badge.py`, `stat_badge_bf_x8.png`, `stat_badge_log2map_x8.png`, `stat_badge_map.txt` | STAT badge in BF colours and on the LoG II palette |
| `bible_rows.md` | 25 BFP rows for sections 5b, 7 and 14 |
