## Section 4

| fact | tags | confidence | tag | id |
| --- | --- | --- | --- | --- |
| **Set 132 is byte identical to set 129, and set 133 to set 130.** All 288 shared records (260 for the Super Saiyan pair) name the SAME record header addresses, and no pixel differs. Validated against a control: set 128 against set 129 shares ZERO headers and differs in 280 of 288 frames, so the comparison does detect a real difference. The bible's "post-Cell" label on 132 and 133 describes a use, not different art | #sprite char:trunks set:129 set:130 set:132 set:133 | C (manifest walk plus pixel compare, with control) | TKS | |
| Set 131 exports to 12 unique frames over 40 records, anims 0, 1 and 4 only, and its anim 0 shares one frame across dirs 0 and 1. Exported 2026-11-08 to `art\vanilla-sets\set131`; it was the only Trunks set never exported | #sprite char:trunks set:131 | C (export) | TKS | |
| Set 135 is KID or TEEN Trunks (owner, 2026-11-08), not an adult variant. 102 unique frames over 180 records, anims 0-3, 5-10, 12 and 13. It is appearance entry 18 and has no transform | #sprite char:trunks set:135 | C (export counts), owner (who it is) | TKS | |

## Section 6

| fact | tags | confidence | tag | id |
| --- | --- | --- | --- | --- |
| **The appearance entry's byte +1 is the SET ID and its byte +4 is the TRANSFORM TARGET entry.** Table `rom:0x1D967C`, 20 byte entries. Byte +0 is the form flag (0x00 base, 0x01 super), byte +2 the dialog portrait, and the word at +16 the form object. Entry 13 is `00 81 64 14 ...` = base, set 129, portrait 100, target entry 14. Entry 15 is `00 84 64 14 ...` = base, set 132, portrait 100, target entry 16 | #form #sprite | C (table bytes, reconciled with B0458, B0642 and B2193) | TKS | |
| **Entries 13 and 15 differ in exactly one field, the transform target, so the ONLY difference between armoured Trunks 129 and 132 is which Super Saiyan GRADE they become.** Entry 14 (set 130) carries form object `0x030021E8`, the ascended grade: +15 STR, +10 POW, +15 END and slower movement (B0427). Entry 16 (set 133) carries `0x030021EC`, the ordinary grade: +10 to each core stat (B0426). Vegeta is wired the same way, entry 10 ascended and entry 11 ordinary (B0459) | #form char:trunks char:vegeta set:129 set:130 set:132 set:133 | C (table bytes, with B0426, B0427, B0459) | TKS | |
| **The game has an ascended Super Saiyan GRADE already wired, with no distinct art.** Both ascended entries (Trunks 14, Vegeta 10) point at sprite data byte identical to the ordinary grade's. So the stat bonus, the speed penalty and the transform plumbing all exist and are reachable; only the bulked sprites were never drawn. An ascended form feature therefore needs new art and a set id swap, not new form code | #form #sprite #decision char:trunks char:vegeta | C (pixel compare plus table bytes) | TKS | |
