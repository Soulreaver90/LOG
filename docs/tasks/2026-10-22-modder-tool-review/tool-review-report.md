# Tool review: Webfoot audio tool, Sprite Swapper, Buu's Fury compressor

Date: 2026-10-22. Brief: `docs\tasks\2026-10-22-modder-tool-review\tool-review.md`. ROM under test: r27 (`builds\log2_poc_r27.gba`, SHA-1 `5c4befd8feb8a8840730882c330f3c1ed5d1e51c`), read from a byte copy in `scratch\rom-copies\toolreview\`.

Labels: **C** = CONFIRMED (quoted code or bytes), **L** = LIKELY, **S** = SPECULATIVE. Paths in `file:line` form are inside the clone named in each section.


---

## 1. Verdicts

| Tool | Verdict | Main reasons |
|---|---|---|
| Webfoot Audio Engine (`webfootaudioengine` 1bb0085) | **Use with limits** | Its parser fits LoG II (L). It never searches for free 0xFF space, so it cannot allocate into our reserved regions (C). But it appends past 16 MB (C), it needs NumPy (not installed), it has no license, and add-slot rewrites ROM words found by a byte search (C). Run it only on a copy of a finished build, as the last step, with the flags in section 2.7. |
| Sprite Swapper and Image Extractor V1.0.1 | **Do not use** | Closed Windows `.exe` files in a `.rar`, no source, no license, no digest (C). It is built for unmodified ROMs (C, README). Its free-space choice for "larger sprites" is unknown and can land in our 0xFF regions (S). We now have everything it offers that we need: export (ours) and a verified compressor (section 4). |
| Buu's Fury compressor (`webfoot_lz.py` `pack()`) | **Use now, with limits** | Pure Python, no I/O (C). 1,656 of 1,656 real r27 frames round-trip through our decoder (C). Limits: call it with `kind=1`; keep the MPL-2.0 notice; output is 4-6 % larger than the original streams; use its encoder only, not its decoder. |

---

## 2. Webfoot Audio Engine

### 2.1 What each code path writes

| Path | What it reads | What it writes | Label |
|---|---|---|---|
| `scan` | The ROM (`rom.py:36-40`, `open(path, 'rb')`) | One file: `<--out>\<rom name>\discovery.json` (`cli.py:194-196`, `write_json`); `io.py:20-24` creates the parent folder | C |
| `import-it`, replace mode | The `.it` file and the target ROM, both read into memory (`it_support\public.py:73`, `:84`) | One output ROM (`public.py:100`) and an optional JSON report (`:110-111`). In the ROM: the song blob, a 64-byte aux block, new samples and a sample table, all appended at the end (`it_support\patcher.py:108`, `:118`, `it_support\samples.py:235`, `:272`); then the 20-byte descriptor of the target slot is overwritten in place (`rom_support\table_ops.py:325-326`) | C |
| `import-it --add-slot` | Same | Same appended data, plus a new copy of the whole music table at the end (`table_ops.py:200-201`), every byte-offset match of an old descriptor pointer rewritten (`debug_patches.py:72-75`), the old table filled with 0xFF (`table_ops.py:217-220`), and up to three "debug" patches (`table_ops.py:221-241`) | C |
| `rom_support\debug_patches.py` | Output buffer | `_patch_debug_music_count_bound` (`:120-203`): finds a Thumb `ldr` of the new table pointer followed by `83 00 18 18 80 00 41 18`, then a `cmp rX,#imm ; bge ; add #1 ; str` within 128 bytes before it, and writes the new maximum index into the cmp byte (`:190`). `_patch_debug_music_byte_selector_bounds` (`:206-318`): same idea for an `ldrb ; cmp ; b ; add #1 ; strb` shape (`:305`). `_patch_debug_last_descriptor_refs` (`:345-427`): repoints literals of the last descriptor to the new last one; its fallback test `return int(load_offset) < int(literal_offset)` (`:342`) is true for almost every Thumb literal load | C |

What add-slot does to r27 (my transcription of the same searches, `scripts\one-time\2026-10-22-modder-tool-review\audio_probe.py`, output `out\audio_probe_r27.txt`):

- Descriptor pointer matches: 7, all 4-aligned, all Thumb literal-pool words in the base 8 MB: song 0 at `rom:0x5B44`, `0x9E1C`, `0xC580` (loaded at `@0x08005906`, `@0x08009C9E`, `@0x0800C4FA`), song 15 at `rom:0x208`, `0x630`, `0x1EDD8`, song 21 at `rom:0xF780`. None in the expansion area or `ART_REGION`. **C**
- Count patch: one byte, `rom:0x58F4` `0x2B` to `0x2C`. This is the sound test bound (`@0x080058F4 cmp r0,#0x2b`). **C**
- Selector patch and last-descriptor patch: no match in r27. **C**
- Old table `rom:0x1D4B2C`-`0x1D4E9B` (880 bytes) becomes 0xFF. **C**

### 2.2 How it chooses space (the reserved-region question)

It does not choose free space. Every allocation appends at the end of the file:

```python
def _reserve_append_space(buffer: bytearray, size: int, alignment: int = 4) -> int:
    start = _align(len(buffer), alignment)
    _ensure_size(buffer, start + size)
    return start
```
(`rom_support\shared.py:36-39`; the `_with_mod` variant at `:42-54` does the same.) All music, aux, sample and table writes call it: `it_support\patcher.py:92`, `:108`, `:118`; `it_support\samples.py:235`, `:272`, `:382`, `:528`; `rom_support\table_ops.py:200`; `rom_support\importer.py:87`, `:116`, `:136`, `:140`, `:144`; `rom_support\samples.py:151`; `rom_support\song_codec.py:254`. **C** (search shape: `_reserve_append`; a writer that computes an offset another way would not appear, but every `dst_rom[...] =` site in these files was also listed and each writes at an offset returned by these calls, an existing descriptor or a pointer hit).

Consequences for our build:

- The portrait slots `rom:0xF00000 + 0x1008 x id` (unused ids 0xFF), the `art_inject` `LEGACY_GAP` at `rom:0x895468` and the allocator space are never allocation targets. **C**
- Input 16 MB means output larger than 16 MB. `log2_build.assemble` refuses that (`log2_build.py:61-62`), so the tool cannot run inside our build. It must run after it. **C**
- Writes inside the first 16 MB are limited to: the replaced descriptor (replace mode), or the 7 pointer words, the 0xFF fill and the cmp byte (add-slot). The byte search in `debug_patches.py:27-36` steps one byte at a time (`start = pos + 1`), so a future frame or portrait whose pixels happen to contain `2C 4B 1D 08` (or another descriptor pointer) would be rewritten too. r27 has none. **C** for r27, **S** for later builds.
- A ROM larger than 16 MB cannot be shipped as an IPS patch: IPS offsets are 3 bytes. Use BPS or UPS. **C** (IPS format).
- Save chip: LoG II uses EEPROM (bible section 7). GBATEK says a cart with more than 16 MB of ROM sees the EEPROM only at `0x0DFFFF00`-`0x0DFFFFFF`. I found no `0x0DFFFF00` literal in the base code. Whether saves still work in mGBA and on a flash cart with a 16 MB+ ROM is untested. **S**

### 2.3 Network, subprocess, writes outside the output

- No network code on the CLI paths. `webbrowser`, `http.server` and `urllib` appear only in `web_support\server.py` and `web_support\common.py` (imports at `server.py:10-13`, `common.py:10-12`). **C**
- `subprocess` appears only in `build_webapp.py:9`, `:143`, `:273` (PyInstaller and appimagetool). Not run. **C**
- File writes: `io.py` helpers, plus `Path(...).write_bytes` at `it_support\public.py:100`, `:416`, `rom_support\importer.py:409`, `sfx_support\importer.py:585`, `:692`, WAV writers at `parsers.py:389`, `render_support\it_playback.py:333`, `web_support\sfx.py:377`, and blob dumps at `extract.py:261-270`. Each goes to a path the user gives, or a default (see 2.7). **C**
- Defaults that matter: without `--out`, `import-it` writes next to the target ROM (`public.py:76-82`, `:42-56`). Replace mode without `--target-slot` replaces slot **1** (`patcher.py:60`). **C**

### 2.4 Does it find LoG II's tables?

I could not run `scan`: `rom.py:8` imports NumPy at module level, and NumPy is missing under `py -3 -I` (`ModuleNotFoundError: No module named 'numpy'`). Per the brief I stopped the run. I transcribed its checks into my own script instead (`audio_probe.py`, sources listed in its header):

| Check | r27 result | Label |
|---|---|---|
| Webfoot-format candidates with 4+ entries, ranked by pointer hits (`music_tables.py:86-139`) | One: `rom:0x1D4B2C`, 44 songs, 3 pointer hits | L |
| 20-byte parser (`parsers.py:203-241`) at `rom:0x1D4B2C` | 44 of 44 entries pass | L |
| Sample directory (`parsers.py:339-367`) at `rom:0x14A8A4` | 101 entries | L |
| Pitch, damping, LFO prefixes (`music_tables.py:262-269`; a missing one raises) | `rom:0x7FCC1C`, `0x7FC93C`, `0x7FCE9C`, `0x7FD09C` | L |
| Timer reload (`music_tables.py:236-259`) | `0xFFFFFBE6`, so 15,978 Hz | L |

`discover_all` (used by `scan` for `music_banks`) also tries 1-3 entry tables that pass a song decode (`music_tables.py:219-226`). I did not transcribe that decoder, so the bank count in a real `scan` may be higher than 1. **S**

Against the bible:

| Bible (rows 643, 686) | Tool's parser | Agreement |
|---|---|---|
| 44 x 20 B at `@0x081D4B2C` | 44 x 20 B "WebfootFormat" | Yes (L) |
| +0, +4 pointers | +0 track table (pattern pointers), +4 sequence (order list, 0xFF end) | Yes; the bible did not name them |
| +8 = `0x0814A8A4`, 12-byte sample directory, 101 slots | +8 sample table, `{ptr, u32 (flags | loop_start << 16), u16 length, u16 base_pitch}`, 101 kept | Yes (row 686 "music record +8 sample directory" is right) |
| +0xC = `0x0814AD60` | +0xC "aux" table, indexed by (event byte >> 4) - 2 (`parsers.py:453-465`), so 14 bytes are used. Song 0's sequence starts at `0x0814AD6E` = aux + 14 | Yes; size 14, not the tool's `AUX_TABLE_SIZE` 64 |
| u16 +0x10 `0x341`-`0x68C`, +0x12 = 0 | low byte tempo (65-140), high byte speed (3, 4 or 6) | Yes |
| 15 channels (`@0x08020A4C`) | `SONG_VOICE_COUNT = 15` (`constants.py:16`) | Yes |

### 2.5 The song in Gohan's Rage scene

- Scene table `rom:0x3EA400` (Cell Jr type 26 event, map 14,3). Record 26, seq 27, `rom:0x3EA33C`, starts `1B 00 00` then `00 14 02 31` = `push 20 ; ext 49` at `rom:0x3EA33F`. It runs right after Gohan's line "I won't watch this ANYMORE!!!!!!" and before the SSJ2 change `push 0 ; push 160 ; ext 73`. The r27 table word is `0x083EA33C` (not relocated). **C** (bytes)
- Seq 1 of the same table (relocated to `rom:0x89A71C` in r27) plays music 37 when the scene opens. The next music command in the stretch is music 17 in `rom:0x3EB704` seq 1 (r22 dump `scripts\one-time\2026-10-20-cellgames-ssj\scenes_r22.txt:197`). **C**
- So the Rage song is **music 20** (descriptor `rom:0x1D4CBC`, tempo 90, speed 6). The wiki row in bible section 10 names sound test track 20 "Super Saiyan Rage". That music 20 is what plays through the Rage fight is **L** (not heard in mGBA).
- Music 20 has one script user: byte shapes `00 14 02 31` and `01 28 02 31` find only `rom:0x3EA33F`; no map entry has +0x24 = 20; code literals name songs 0, 15 and 21 only. A computed music id would not appear. **L**

### 2.6 MIDI workflow (my "Gohan Angers" MIDI)

Two ways in, both on a copy of the finished build:

| Option | ROM changes inside 16 MB | Notes |
|---|---|---|
| A. Replace slot 20 | 20 bytes at `rom:0x1D4CBC` | Simplest. Affects only the Rage scene (L, 2.5). No pointer rewrite, no debug patch. |
| B. Add slot 44, then point the Rage record at it | 7 pointer words, 880 bytes of 0xFF, `rom:0x58F4`; plus our one-byte script patch `rom:0x3EA340` `0x14` to `0x2C` | Keeps the vanilla Rage song. Only append at the end: inserting before 44 shifts every later music id, and scripts are not patched (only descriptor pointers are, `debug_patches.py:66-81`). |

Steps:

1. In OpenMPT, load the MIDI and save as `.it`. Keep these import limits (`it_support\compat.py`, `loader.py`, README "Import Notes"):
   - At most 15 channels that play notes (`compat.py:348-352`).
   - Effects A, B, C, D, E, F, G, H, K, L, O, Q, SDx only, T, U, X (`compat.py:34`, `:92-111`). Any other effect stops the import. The README lists "Dxx pattern break"; the code passes C as pattern break and D as IT volume slide.
   - Volume column: plain volume 0-64 only, no slides or pan (`compat.py:329-334`).
   - No "+++" skip orders (`public.py:74-75`). At most 255 rows a pattern (README).
   - Samples become 8-bit mono, at most 65,534 bytes; C5 speed becomes the base pitch, clamped to 65,535 Hz (`loader.py:251-255`, `:285`). Envelopes and NNA are not carried over (L, no reader found).
2. To reuse LoG II's own instruments: first run `extract-it` on a copy of r27 (for example song 20). The `.it` it writes holds the ROM samples as 8-bit signed data with C5 = base pitch and the ROM loop points (`export_support\builder.py:144-175`). Build the arrangement inside that module, or copy its samples into the MIDI module. Do not resample, normalize, trim, change loops or convert them to 16-bit. On import, a sample is reused only when its bytes, length, loop start, loop flags and base pitch all equal a ROM sample (`it_support\samples.py:84-109`, `:201-233`); otherwise a new copy is appended. The import report gives `reused_sample_count`. **C** (code), **L** (that exported samples match exactly on LoG II).
3. Import, on a copy, with every flag explicit:
   - A: `py -3 -m webfoot_audio import-it rage.it <copy of build>.gba --out <scratch>\rage_test.gba --target-slot 20 --report <scratch>\rage_import.json`
   - B: same with `--add-slot` and no `--target-slot`, then the one-byte script patch.
4. Check the report: `pointer_hits` (add-slot) must list only the 7 offsets in 2.1; `output_size` grows past 16 MB.
5. Test in mGBA: the Rage scene, the sound test (debug menu, track 20 or 44), a save and a reload.

Every rebuild with `log2_build` drops the import. Re-run it on each new build, never on an output that already has the song.

### 2.7 Coordinator add-on: the web UI `.it` preview

| Question | Answer | Label |
|---|---|---|
| Binds to | `127.0.0.1:8765` by default (`cli.py:179-180`, `server.py:697-698`); `--host` can change it. It opens the default browser (`server.py:701-702`; `--no-open` stops that) | C |
| Reads | Any path typed into the page: `.it` (`server.py:374-379`), ROM (`:381-399`), WAV (`:458-465`). `/api/browse` lists any folder on the PC (`common.py:249-286`) | C |
| Writes (preview) | Nothing on disk. Preview bytes go to in-memory caches served at `/it/<token>/` and `/audio/<token>/` (`server.py:62-92`, `:333-372`) | C |
| Writes (other buttons) | Export to the chosen folder (default `out` under the current folder, `server.py:469`, `:479`). Import IT needs an explicit output path (`:616-618`). Import SFX defaults the output to the input ROM, so it overwrites the ROM in place (`server.py:538`, `:581`) | C |
| Access control | None: no token, no Origin or Host check, and the JSON body is parsed whatever the Content-Type (`server.py:184-192`). While it runs, any web page open in the same browser can send POSTs to it (blind cross-site requests that export or import). A DNS-rebinding page could also read `/api/browse` results | L (standard browser behavior, not tested) |
| Internet | One load: `@import url("https://fonts.googleapis.com/css2?...")` (`web_support\assets\index_parts\theme_shell.css:1`), which also pulls font files from Google. React, chiptune3 and libopenmpt come from the local `web_vendor` folder (`index.html` script tags, `server.py:297-313`). No other external URL in the page scripts or the player files | C |
| Engine fidelity | Generic tracker playback. `/api/prepare-it` serves the `.it` bytes unchanged (`server.py:374-379`); the page loads them into chiptune3 0.8.6 with libopenmpt (`browser_playback.js:175`, `:257`, `:458`). Nothing applies the Webfoot limits: no 15-channel check, no effect filter, no 8-bit mono conversion, no 15,978 Hz mix. A song can preview well and still fail import or sound different in the game | C |

Safe to run here? With limits: only after I install NumPy (in a venv), start it with `--no-open`, open the page in one browser, close other sites while it runs, never use Import SFX without an output path, and stop the server after use. The vendored 1.7 MB `libopenmpt.worklet.js` and the React development builds were not compared with upstream releases. **L**. For a true preview, import into a scratch copy and play it in mGBA.

### 2.8 License

No license file: by default all rights are reserved. Running it privately is my call. Do not copy its code into our repo or scripts. The ROM data it writes from my MIDI is not its code. **C** (no LICENSE in the clone), **S** (legal reading).

---

## 3. Sprite Swapper and Image Extractor

Sources: README in `Documents\GitHub\Sprite-Swapper-Image-Extractor` (commit dfd4b75) and `gh release view` (tag V1, asset `Sprites.Swapper.v1.0.1.Images.Extractor.rar`, 31,718,696 bytes, 59 downloads, digest null, repo license null). Nothing downloaded or run.

### 3.1 What it does that our tools do not

| Feature (README) | Ours | Label |
|---|---|---|
| Re-insert edited art compressed (`jcalg1.exe`) | Raw type 0 only, until now. `pack()` (section 4) closes this gap | C |
| BMP export plus `infos.json` (offset, size, palette) for LoG II and Buu's Fury, including "manual extraction" by offset and tilesets "without CRC32 constraints" | `webfoot_decompress.py set` and `log2_sprites.py export` write PNGs for LoG II sprite sets; no Buu's Fury palette sets, no tileset export | C |
| IPS patch output, timestamped export folders, `.SAV` copy | Not in our tools | C |
| Mirrored sprites (V1.0.1) and sprites larger than the original (credit "Zhacks") | We clone sets and frames by allocation (`clone_set`, `art_inject`) | C |

### 3.2 Is our codec JCALG1?

Yes for the bitstream, no for the container. Upstream `jeremycollake/jcalg1` `jccomp.inc` (fetched 2026-10-22) has `INITIAL_BASE equ 8`, `DecrementIndex1 = 027fh`, `DecrementIndex2 = 037ffh`, `DecrementIndex3 = 010000h`, `SHORT_RANGE = 1111111b`, `SHORT_BITS = 7`, `ONEBYTE_PHRASE_BITS = 4`, `LITERAL_BITSIZE = 1`, `BLOCK_SIZE equ 256`. Each equals a value in the LoG II ARM routine (`re-sprite-decompression.md` stream table; `scripts\one-time\2026-10-16-first-probes\dis_iwram.txt`): offset width 8, length bonus at 0x27F, 0x37FF and 0x10000, 7-bit short match, 4-bit one-byte phrase, literal width 7 + 1 bit, 256-byte raw block. The `jcalg1_d.asm` summary has the same tag set (1 literal, 01 gamma phrase with last-index reuse, 000 short match with end and width codes, 001 one-byte phrase with literal-size and raw-block codes). **C** for the constants and tags, **L** for bit-for-bit identity (I read `jcalg1_d.asm` only as a summary). JCALG1's own header is `{u16 'JC', u32 size, u32 checksum}`; LoG II frames use `{u32 type, u32 size}`. So the swapper must strip JCALG1's header and write the Webfoot one. **L** (no source).

### 3.3 What "larger sprites than the original" implies

- A larger packed stream cannot stay in place. It must go to new space, with the frame record +8 pointer moved. The base 8 MB has no usable free space (bible section 2), so on a vanilla ROM the tool must expand the ROM or reuse 0xFF runs. **L**
- On our build, every free byte is 0xFF: unused portrait slots in `ART_REGION`, `LEGACY_GAP` at `rom:0x895468`, and the allocator tail. A tool that looks for 0xFF runs would write there. Its method is unknown. **S**
- Larger dimensions also hit fixed limits: the upload unpacks to a 0x1000-byte stack buffer (`@0x08007772`) and the set header slot size is 0x400 for sets 53-59. Its known issue "a 64x64 sprite into a non-64x64 slot crashes" fits a 4,096-byte frame in a 0x400 slot. **L**
- The README requires an original ROM and a fresh `infos.json` per ROM, so running it on our build is outside its design. **C** (README)

---

## 4. Buu's Fury compressor (`tools\webfoot\webfoot_lz.py`)

### 4.1 Safety

479 lines, imports only `dataclasses` and `struct` (`webfoot_lz.py:2-5`). No file, network or subprocess calls. **C**. The file has no license header; the repo LICENSE is MPL-2.0 and `NOTICE:12-15` names the file. I copied lines 8-9, 22-23 and 313-479 verbatim (diff-checked) to `scripts\one-time\2026-10-22-modder-tool-review\vendor\webfoot_lz_pack.py` and added the MPL-2.0 notice with the source commit.

### 4.2 What `pack()` emits

From `webfoot_lz.py:375-479`: header `{kind, len}`, then `001 0000 0 1` (8-bit literals, base 0), then per token: literal `1` + 8 bits; one-byte phrase `001` + 4 bits (distance 1-14); short match `000` + 7-bit offset + 2-bit length (2-5); repeat offset `01` + gamma(2) + gamma(length); long match `01` + gamma((d >> 8) + 3) + 8 bits + gamma(length - bias); end `000 0000000 00`; zero padding to a 32-bit word. Never: raw blocks, offset-width changes, a 7-bit literal mode, or nibble value 1. Window 0xFFFF, longest match 255. Default kind is 2. **C**

Each of these codes matches the ARM routine (`dis_iwram.txt`): literal `@0x03000014`, one-byte phrase `@0x030000E8`, short match `@0x030000F0`-`@0x03000118` (sets r12), repeat `@0x03000170`, long match `@0x030001A8`-`@0x03000220` with the same bonus ladder, end `@0x0300011C`-`@0x03000128`. **C**

Limit: use `kind=1`. The remap dispatcher `@0x0801F3BA` does not unpack type 2 (bible section 14). **C**

### 4.3 The decoder differences named in the decomp review

| Difference | ARM `@0x03000000` | Ours | Theirs | Effect on `pack()` |
|---|---|---|---|---|
| Literal before the mode code | Reads r3 bits + r4; through `@0x0801F394`, r3 = frame type (1 or 2), r4 = caller's value | Raises an error | Width = type, base 0 (`:253-258`) | None: `pack()` sets the mode first |
| Raw run per continue bit | 256 bytes (`@0x03000088` `mov r9,#0x100`) | 256 (`webfoot_decompress.py:136-139`) | 2 (`:187-192`): wrong for LoG II | None: never emitted |
| Nibble value 1 (new, not in the decomp review) | Writes 0 (`@0x03000068` `subs r7,r7,#1 ; beq`) | Writes 0 | Writes `literal_base` (`:177-184`): wrong after a 7-bit mode | None: never emitted |

All three are **C** from the disassembly. Our decoder is the reference; do not use their `unpack()` on LoG II data.

### 4.4 Round trip

`scripts\one-time\2026-10-22-modder-tool-review\roundtrip.py` (`py -3 -I -B`, 3.9 s; table `out\roundtrip.csv`): decode the original frame with our decoder, `pack(payload, kind=1)`, decode the result with `webfoot_decompress.unpack_frame`, compare.

| Group | Equal | Stored now | `pack()` | Ratio |
|---|---|---|---|---|
| Dialog portraits, type 1 (ids 26-121 from the live block `rom:0x894EAC`) | 86 / 86 | 90,352 B | 94,200 B | 104.3 % |
| Dialog portraits, type 0 raw (`art_inject` slots) | 10 / 10 | 41,040 B | 10,752 B | 26.2 % |
| Sprite frames, type 1 (sets 53-61, 103, 157-160 in full, every 25th unique frame of the rest) | 1,560 / 1,560 | 417,544 B | 442,948 B | 106.1 % |
| Synthetic: empty, 1 byte, 4 KB zeros, 4 KB ramp, 4 KB random, 70,000 bytes | 6 / 6 | | random 4 KB = 4,564 B (worst case +11 %) | |

**C**: 1,662 of 1,662 equal. The ARM routine has no output bound, so a packed frame must still unpack to at most 0x1000 bytes for the sprite path.

### 4.5 Is it JCALG1 too?

It writes a JCALG1-compatible bitstream subset inside a Webfoot header (section 3.2). It is not Collake's encoder: it is a greedy parse with a 32-entry hash chain, and its output is 4-6 % larger than the shipped streams. The decomp's claim that `compress.exe` (built from jcalg1) rebuilds the assets byte for byte fits the shipped streams being JCALG1 output. **L**

---

## 5. Top risks

1. **Audio tool grows the ROM past 16 MB.** Our build refuses that size; IPS cannot carry it; EEPROM saves on 16 MB+ are untested (S). Run it last, on a copy, and ship BPS.
2. **Add-slot byte search.** It rewrites any byte-offset match of a descriptor pointer anywhere in the ROM. Today: 7 correct hits. Check `pointer_hits` in the report on every run.
3. **Wrong defaults.** Replace mode without `--target-slot` hits slot 1; no `--out` writes next to the input; web Import SFX overwrites the input ROM.
4. **Web UI has no access control** while it runs (L), and loads Google Fonts.
5. **Preview is not the engine.** libopenmpt plays the `.it` as a generic tracker.
6. **Sprite Swapper**: unauditable binaries; unknown free-space method on our 0xFF regions.
7. **`pack()` default kind 2** would break remapped sprites; always pass `kind=1`.

---

## 6. Open points

1. `scan` not run: NumPy is missing under `-I`. If I install NumPy in a venv, rerun `scan` on `scratch\rom-copies\toolreview\log2_poc_r27.gba` with `--out scripts\one-time\2026-10-22-modder-tool-review\out` to confirm 2.4 and the bank count.
2. Test a 16 MB+ ROM in mGBA (and my flash cart): boot, save, reload.
3. Long term: copy the tool's appended song and sample blobs into our allocator space with our own patch (pointer fix-ups), so the ROM stays 16 MB and survives rebuilds. That uses its output, not its code.
4. Whether LoG II samples exported by `extract-it` re-import as "reused" is not proven on this ROM.
5. Hear the Rage scene in mGBA to confirm music 20 plays to the end of the fight.
6. The decomp review cites `NOTICE:144-147`; `NOTICE` has 18 lines. The jcalg1 and `webfoot_lz.py` notes are at `NOTICE:6-9` and `:12-15`.
7. Read `jcalg1_d.asm` in full (not a summary) to move the JCALG1 identity from L to C.

## 7. Files

| File | Purpose |
|---|---|
| `scratch\rom-copies\toolreview\log2_poc_r27.gba` | Byte copy of r27 (same SHA-1) |
| `scripts\one-time\2026-10-22-modder-tool-review\vendor\webfoot_lz_pack.py` | Verbatim `pack()` with MPL-2.0 notice |
| `scripts\one-time\2026-10-22-modder-tool-review\roundtrip.py`, `out\roundtrip.csv` | Round-trip test and per-frame results |
| `scripts\one-time\2026-10-22-modder-tool-review\audio_probe.py`, `out\audio_probe_r27.txt` | Transcribed table checks and add-slot hit scan |
| `scripts\one-time\2026-10-22-modder-tool-review\bible_rows.md` | Rows for sections 3, 8, 10, 10a, 14 |
