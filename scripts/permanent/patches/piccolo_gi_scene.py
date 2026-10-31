r"""
piccolo_gi_scene.py - Patch: on Dende's Lookout, Piccolo gives Super Saiyan Gohan his gi (my storyboard r29-r32).

Usage:   py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r32.gba
Input:   the ROM after fullpower_ssj (r28). Run it right after fullpower_ssj, so no earlier allocation moves.
r30:     Gohan and Goku walk in (ext 53, not ext 54: ext 54 sets state 12, the flying anim); "You were my first
         teacher." ends in a period.
r31:     Piccolo and Gohan stay through the walk-offs (only Trunks and Vegeta fly off) and are moved, not spawned,
         for the new scene (ext 62). After "You look great Gohan" both fly off screen downward (ext 54, the
         vanilla walk-off direction) and are removed; Goku keeps his spot and the follow camera takes over from
         the scene camera (no fade, no cut back). Records 31 and 44 keep their r30 slot sizes, so no later
         allocation moves.
r32:     The vanilla lines "Goku is now an available character! / You are now playing as Goku." (index 30) and
         their chime (sound 28) show after the fly-off, right before "Journal Updated!". Table word 29 names the
         walk-offs copy, so index 28 skips the lines; record 44 ends with the chime and goes to index 30; the
         lines go on to index 31, now a tail record (SET 158, sound 62, the Journal chime) in the free end of
         r31's record 31 slot. The party change and Goku's lead stay in seq 27, before the scene. No address moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["piccolo_gi_scene"]. scene() and TEXTS hold the
         new records, so tests read the design from one place.
Method:  The chamber exit is one scene table (rom:0x3DBDD4, 34 records and an END word), started only by the two
         type 5 records whose +4 words are rom:0x3CF7E4 and rom:0x3D1530. The patch copies the table to the
         expansion area, appends records 35-44 and points both type 5 words at the copy. Words 2, 15, 20 and 29 of
         the copy name edited copies; the old table and records stay unchanged (a state paused in the old scene
         ends it):
         - seq 3: NPC Gohan set 56 to 59 (armor Super Saiyan); Gohan's record write ext 73 (0, 158) becomes
           ext 73 (0, 53), entry 0, so the cutscene portrait hook leaves raw 62 (armor Super Saiyan) as it is;
         - seq 16, 21 (Gohan's lines): raw portrait 121 to 62;
         - seq 32 (copy at word 29): the Trunks and Vegeta walk-offs only, next index 35. Its tail is split:
           the camera follow goes to record 44, SET 158 and sound 62 to record 31.
         New: 35 fade out, Piccolo moved near the left edge facing right, Gohan moved off screen, fade in, Gohan
         walks in; 36-39 the four lines; 40 Piccolo raises his arm (state 11) during three blue flashes (ext 135),
         Gohan 59 out, 158 in, ext 73 (0, 158), Gohan admires the gi (state 4); 41 "Thank you, it's awesome!";
         42 Goku (the player) walks in; 43 "You look great Gohan"; 44 Piccolo and Gohan fly off and are removed,
         camera on Goku, sound 28; then the vanilla lines (30), 31 SET 158 and sound 62, "Journal Updated!" (32).
Rules:   Source: docs\tasks\2026-10-22-piccolo-gi-scene\piccolo-gi-scene.md (my storyboard), piccolo-gi-scene-report.md (study).
         Every source record, the table and both type 5 words are checked (bytes or SHA-1) before any write; a
         second run raises. Ext ops pop their arguments and push nothing, so each code record ends with an empty
         stack (one value left would replace the next index).
"""
import hashlib
import struct

from scene.scene_lib import relocate

# ===== constants =====
ROM_BASE = 0x08000000
TABLE, TABLE_WORDS, TABLE_SHA1 = 0x3DBDD4, 35, "a9d3c557eb06d09555dc94a1aa5097e883b70528"   # 34 records + END
TYPE5_WORDS = (0x3CF7E4, 0x3D1530)                    # +4 of the type 5 records rom:0x3CF7E0, rom:0x3D152C
REVERSE_LITERAL, ENTRY = 0x42F0, 20                   # reverse lookup copy: entry e +1 is the set ext 73 names
ARMOR_SSJ, GI_SSJ, PICCOLO, DEMON = 59, 158, 103, 53  # sets
FIRST_NEW, LAST_NEW, JOURNAL = 35, 44, 32             # new table indexes; seq 33 "Journal Updated!" is index 32
WALK_OFFS_AT, LINES_AT, TAIL_AT = 29, 30, 31          # index 28 goes to 29; the vanilla lines record goes to 31
CHIME_RECORD = (0x3DBD10, "1e0000001c022e11")         # vanilla word 29: sound 28 ; next 30 (left unused)
LINES_HEAD = (0x3DBD18, "1f000200")                   # vanilla word 30: next 31, type 2, no portrait
SYSTEM_CHIME, JOURNAL_CHIME = 28, 62                  # vanilla plays 28 before "@^" lines, 62 before the Journal

# table index: (record, length, SHA-1 of the r28 bytes)
SOURCES = {2: (0x3DB59C, 0xCC, "5e92ee50d43e4913930bcd448e1f72d770128aa2"),     # seq 3
           15: (0x3DB930, 0x64, "beed617bb64ce66fe37c6f3cf019dbbbf4e5bed5"),    # seq 16, type 2
           20: (0x3DBABC, 0x54, "afad60b0a6cc6ebaee5cb4bd6b8235d70b1fe25a"),    # seq 21, type 2
           31: (0x3DBD5C, 0x57, "7314f769d4fb82bbc176ad22d8ea12f1a6eb5e5e")}    # seq 32
SEQ3_EDITS = {0x3DB5D0: ("1d03708d108660", "1d03768d108660"),   # push 56,840,432 ; ext 51 (spawn)
              0x3DB5D9: ("1d027002", "1d027602"),               # push 56,1 ; ext 55
              0x3DB629: ("009e", "0035")}                       # push 0 ; push 158 ; ext 73
SEQ32_TAIL_AT = 0x3DBDA6
SEQ32_TAIL = bytes.fromhex("00000221" "009e021b" "003e022e" "11")  # ext 33 (0) ; SET 158 ; ext 46 (62) ; end
SEQ32_DROPS = {0x3DBD5F: ("001a022e" "1d03708d1087400236" "00380234", ""),     # sound 26 ; Gohan flies, leaves
               0x3DBD94: ("001a022e" "1d03814e8c4087300236" "00670234", "")}   # sound 26 ; Piccolo flies, leaves
GOHAN_LINE_PORTRAIT = (121, 62)                                 # seq 16, 21 record +3
# Slot sizes that keep every r30 address: r30's 75-byte record 31 slot holds the walk-offs and the r32 tail
SLOTS = {WALK_OFFS_AT: 40, TAIL_AT: 35, 44: 61}

# ===== the new scene (map pixels; the camera is the top-left of the view) =====
PICCOLO_AT, GOHAN_AT, GOKU_AT = (312, 400), (344, 400), (384, 400)
GOHAN_FROM, GOKU_FROM = (496, 400), (520, 400)
CAMERA, CAMERA_SPEED, FADE, VIEW_H = (232, 320), 40, 30, 160
BLUE, PULSE, PULSES = (72, 160, 248), 32, 3                     # ext 135 colour (RGB888), frames per pulse
RAISE, ADMIRE = 11, 4                                           # ext 57 states: anim 11 arm up, anim 4 pose
LEFT, RIGHT = 2, 3
WALK, FLY, MOVE_TO = 53, 54, 62         # ext 53 walks (anim 1, 1 px a frame); ext 54 flies (anim 12, 2 px a frame)
FLY_SOUND = 26                          # vanilla plays it before each walk-off flight (seq 32)
OFF_SCREEN_Y = CAMERA[1] + VIEW_H + 24  # frames are drawn from y - 24, so at 504 the sprite top leaves the view
TEXTS = {36: (62, "Piccolo, can I have a new outfit just like yours?"),
         37: (3, "..."),
         38: (62, "You were my first teacher."),
         39: (3, "Yeah kid, it will make you look really sharp."),
         41: (115, "Thank you, it's awesome!"),
         43: (65, "You look great Gohan")}          # index: (raw portrait, text); 3 = Piccolo's record (id 90)


# ===== script encoding =====
# Moved to scene_lib. Re-bound here: patches.celljr_fight, patches.chamber_spar,
# patches.chapter_cards, patches.vegeta_19_reveal and patches.vegeta_ssj_scene import them from here.
from scene.scene_lib import code, ext, push, text, zigzag  # noqa: E402,F401


def scene() -> dict:
    """{table index: record bytes} for records 31 (r32 tail) and 35-44; each record's +0 is the next index."""
    nxt = {i: i + 1 for i in range(FIRST_NEW, LAST_NEW)}
    nxt[LAST_NEW] = LINES_AT
    recs = {
        TAIL_AT: code(JOURNAL, ext(27, 158), ext(46, JOURNAL_CHIME)),
        35: code(nxt[35], ext(40, FADE), ext(MOVE_TO, 0, *GOKU_FROM), ext(55, 0, LEFT),
                 ext(31, *CAMERA, CAMERA_SPEED), ext(MOVE_TO, PICCOLO, *PICCOLO_AT), ext(55, PICCOLO, RIGHT),
                 ext(MOVE_TO, ARMOR_SSJ, *GOHAN_FROM), ext(55, ARMOR_SSJ, LEFT), ext(41, FADE),
                 ext(WALK, ARMOR_SSJ, *GOHAN_AT)),
        40: code(nxt[40], ext(63), ext(57, PICCOLO, RAISE), ext(135, ARMOR_SSJ, *BLUE, PULSE) * PULSES, ext(64),
                 ext(52, ARMOR_SSJ), ext(51, GI_SSJ, *GOHAN_AT), ext(55, GI_SSJ, LEFT), ext(55, PICCOLO, RIGHT),
                 ext(73, 0, GI_SSJ), ext(57, GI_SSJ, ADMIRE)),
        42: code(nxt[42], ext(WALK, 0, *GOKU_AT), ext(55, GI_SSJ, RIGHT)),
        44: code(nxt[44], ext(46, FLY_SOUND), ext(63),
                 ext(FLY, PICCOLO, PICCOLO_AT[0], OFF_SCREEN_Y), ext(52, PICCOLO),
                 ext(FLY, GI_SSJ, GOHAN_AT[0], OFF_SCREEN_Y), ext(52, GI_SSJ), ext(64),
                 ext(33, 0), ext(46, SYSTEM_CHIME)),
    }
    for i, (pid, line) in TEXTS.items():
        recs[i] = text(nxt[i], pid, line)
    return dict(sorted(recs.items()))


# ===== checks =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _check(rom: bytearray) -> None:
    for w in TYPE5_WORDS:
        _expect(rom, w, _word(TABLE + ROM_BASE))
    if hashlib.sha1(rom[TABLE:TABLE + 4 * TABLE_WORDS]).hexdigest() != TABLE_SHA1:
        raise ValueError(f"scene table rom:0x{TABLE:X} differs from the r28 bytes")
    for i, (rec, length, sha) in SOURCES.items():
        _expect(rom, TABLE + 4 * i, _word(rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} (table index {i}) differs from the r28 bytes")
    _expect(rom, SEQ32_TAIL_AT, SEQ32_TAIL)
    for at, want in (CHIME_RECORD, LINES_HEAD):
        _expect(rom, at, bytes.fromhex(want))
    reverse = _u32(rom, REVERSE_LITERAL) - ROM_BASE
    for entry, want in ((0, DEMON), (5, GI_SSJ)):           # ext 73 hangs on a set that no entry names
        _expect(rom, reverse + ENTRY * entry + 1, bytes([want]))


def _copies(rom: bytearray) -> dict:
    """{table index: record bytes} for the four edited copies (the walk-offs go to word 29)."""
    rec, length, _ = SOURCES[2]
    out = {2: relocate(rom, rec, length, SEQ3_EDITS)}
    for i in (15, 20):
        rec, length, _ = SOURCES[i]
        data = bytearray(rom[rec:rec + length])
        _expect(rom, rec + 3, bytes([GOHAN_LINE_PORTRAIT[0]]))
        data[3] = GOHAN_LINE_PORTRAIT[1]
        out[i] = bytes(data)
    rec = SOURCES[31][0]
    walks = bytearray(relocate(rom, rec, SEQ32_TAIL_AT - rec, SEQ32_DROPS)) + b"\x11"
    walks[0] = FIRST_NEW
    out[WALK_OFFS_AT] = bytes(walks)
    return out


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "fullpower_ssj" not in alloc.notes:
        raise ValueError("piccolo_gi_scene needs the fullpower_ssj notes: run it first")
    if "piccolo_gi_scene" in alloc.notes:
        raise ValueError("piccolo_gi_scene already ran")
    _check(rom)
    records = {**_copies(rom), **scene()}
    words = [_u32(rom, TABLE + 4 * i) for i in range(TABLE_WORDS)] + [0] * (LAST_NEW + 1 - TABLE_WORDS)

    placed = {}
    for i, data in records.items():
        at = alloc.alloc(max(len(data), SLOTS.get(i, 0)))           # the unused slot tail stays 0xFF
        rom[at:at + len(data)] = data
        placed[i], words[i] = at, at + ROM_BASE
    table = alloc.alloc(4 * len(words))
    rom[table:table + 4 * len(words)] = b"".join(_word(w) for w in words)
    for w in TYPE5_WORDS:
        rom[w:w + 4] = _word(table + ROM_BASE)
    alloc.notes["piccolo_gi_scene"] = {"table": table, "words": len(words), "records": placed,
                                       "sources": {i: s[0] for i, s in SOURCES.items()}}
