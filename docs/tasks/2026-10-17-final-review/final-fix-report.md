# Slice 1 final fix round report


Status: all ten items done. Tests: 77 OK (was 74; 3 new tests plus 2 tightened assertions). Rebuild SHA-1: `345ae98c1145f669d936cad62cad8635467f3824` (unchanged).

| Item | Result |
|---|---|
| 1 Important 1 | Design 8.3 tests 3 and 6 reworded, each with a pass line. |
| 2 Important 2 | Design 8.2 D: Rage aura claim removed, superseding note added (Ruling 31, final decisions). |
| 3 Minor 5 | Plan Tasks 5 and 6 have a "Superseded by rulings" note naming Rulings 13, 18, 19, 27, 30, 31, 35, 36. |
| 4 Minor 1 | `re-sprite-decompression.md`: header +0 is a u16 slot size. Proof: set 56 header at 0x299C48 is `00 04 15 10`, so +1 = 0x04 and u16 = 0x0400. Directions fixed at 4. |
| 5 Minor 2 | `re-outfit.md`: hang fix credited to rom:0x42F0, line 31 answered by re-forms section 2, section 8 questions 1 and 2 quote I line from design 6.6. |
| 6 Minor 3 | `RE-BIBLE.md` flag 195: bytes `00 C3 02 1B` at 0x3EC6A2 (only match in the base 8 MB), ext 35 `02 23` at 0x3EC690. |
| 7 Minor 4 | `RE-BIBLE.md` portrait line marks the old ids as superseded. Final ROM table at 0x8637AC: entry 2 `3B 0A`, entry 5 `73 74`, entry 22 `75 76`. |
| 8 Minor 8 | `build-log.md` has a Task 5 section (offsets, SHA-1 `40d66d64...`, Ruling 35). |
| 9 Minor 6 | `test_portraits.py::test_entries_resolve_to_gi_sets_through_code_literals` (literal rom:0xC804, then rom:0x959C): entries 2, 5, 22 give sets 157, 158, 159. Entry 4 gives set 58 (vanilla word). |
| 10 Minor 7 | `ssj2_form.py` and `gohan_portraits.py` raise `ValueError` naming the patch to run first. One test each, plus the old assertions tightened. |

All edited files: LF, no BOM. Nothing written under `data\`. No ROM byte changed.
