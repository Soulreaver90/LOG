r"""
test_re_tools.py - Tests for the three disasm tools (codemap.py, symbols.py, listing.py) and re_sym.py.

Run (from the scripts\permanent root):
  py -3 -I -m unittest discover -s . -p "test_re_tools.py"
Reads the USA base ROM and scripts\permanent\disasm\data\codemap.json. Builds the code map once (about 7 s). Writes only to a temp folder.
Pinned values come from the disassembly study (docs\tasks\2026-10-18-disasm-study\disasm-study-report.md, sections 3.1 and 5).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PERMANENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PERMANENT))
import log_paths  # noqa: E402

sys.path.insert(0, str(log_paths.DISASM))
import codemap  # noqa: E402
import listing  # noqa: E402
import symbols  # noqa: E402
from patches import ssj2_form, ssj2_idle  # noqa: E402
from rom.re_sym import sym, sym_ptr, sym_rom  # noqa: E402

ROM_PATH = codemap.ROMS / codemap.GAMES["usa"]
MAP_PATH = codemap.OUT_DIR / "codemap.json"


def _lines(target: str) -> dict:
    """{address text: line} for a listing; header lines keyed by their first word after ';'."""
    out = {}
    for line in listing.listing(target, MAP_PATH, ROM_PATH):
        key = line.split()[0] if not line.startswith(";") else line.split()[1]
        out.setdefault(key, line)
    return out


class CodeMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img = codemap.Image(ROM_PATH.read_bytes())
        cls.syms = symbols.for_codemap("usa")
        cls.mp = codemap.build(cls.img, cls.syms)
        cls.cov = codemap.coverage(cls.mp)

    def test_function_count_and_modes(self):
        modes = [f["mode"] for f in self.mp.funcs.values()]
        self.assertEqual((len(modes), modes.count("T"), modes.count("A")), (2264, 2234, 30))

    def test_code_region_and_coverage(self):
        self.assertEqual(self.mp.code_hi, 0x08028724)                     # menu font: first data after code
        c, region = self.cov["counts"], self.cov["region_bytes"]
        self.assertEqual(round(100 * (region - c["unknown"]) / region, 2), 99.40)
        self.assertEqual(self.cov["stray_bl"], 0)
        self.assertEqual(self.cov["iwram_decoded"], 2268)

    def test_every_func_symbol_is_a_start_with_its_mode(self):
        for a, mode in self.syms["functions"].items():
            self.assertEqual(self.mp.funcs.get(a, {}).get("mode"), mode, symbols.name_of(a))

    def test_snapshot_matches_a_fresh_build(self):                       # re-run scripts\permanent\disasm\codemap.py when this fails
        with tempfile.TemporaryDirectory() as tmp:
            codemap.write(self.mp, self.cov, self.syms, Path(tmp), "usa")
            fresh = json.loads((Path(tmp) / "codemap.json").read_text(encoding="utf-8"))
        self.assertEqual(fresh, json.loads(MAP_PATH.read_text(encoding="utf-8")))


class ListingTests(unittest.TestCase):
    def test_get_set(self):
        got = _lines("get_set")
        self.assertIn("0x08009324  Thumb", got["get_set"])
        self.assertIn("cmp r0,#0x7", got["0800934c"])
        self.assertRegex(got["0800959c"], r"\.word 0x083b4e90 +; set_table")
        self.assertTrue(any("; appearance_set" in line for line in got.values()))

    def test_idle_tick(self):
        got = _lines("idle_tick")
        self.assertEqual([got[a].split()[1] for a in ("08007570", "08007572", "08007574", "08007576")],
                         ["488a", "0130", "4882", "0006"])                  # ssj2_idle._expect bytes
        slots = got["vtable"]
        for vt in ("vt_state38+0x4", "vt_state22+0x4", "vt_state0_idle+0x4"):
            self.assertIn(vt, slots)

    def test_portrait(self):
        got = _lines("portrait")
        self.assertIn("bgt 0x800be06", got["0800bdf0"])
        self.assertIn("; portrait_block", got["0800be10"])
        for caller in ("status_page", "dialog_box", "appearance_portrait"):
            self.assertIn(caller, got["callers"])

    def test_damage(self):
        got = _lines("damage")
        self.assertIn("sub r0,r1,r0", got["0800f94e"])
        self.assertIn("mul r0,r5", got["0800f974"])
        self.assertIn(".word 0xfffffd43", got["0800f998"])                 # -701
        self.assertIn(".word 0x0001c3a2", got["0800f99c"])                 # 115618
        calls = " ".join(line for line in got.values() if " bl " in line)
        self.assertIn("rand16", calls)
        self.assertIn("rand_n", calls)

    def test_status_page(self):
        got = _lines("status_page")
        self.assertIn("extent 0x362", got["status_page"])                  # status_bonus.CODE_LEN
        self.assertRegex(got["08003a82"], r"ldr r1,=0x081d967c +; appearance_table")

    def test_appearance_table_refs_are_the_hand_list(self):
        out = listing.refs("appearance_table", MAP_PATH, ROM_PATH)
        self.assertIn("; 18 word(s) in the code region, 0 outside it", out)
        words = {int(line.split()[0][4:], 16) for line in out if line.strip().startswith("rom:")}
        self.assertEqual(words, set(ssj2_form.TABLE_LITERALS) | {ssj2_form.REVERSE_LITERAL})


class SymbolTests(unittest.TestCase):
    def test_names_are_unique_and_json_matches(self):
        self.assertEqual(len(symbols._BY_NAME), len(symbols._BY_ADDR))
        js = json.loads((symbols.OUT_DIR / "symbols.json").read_text(encoding="utf-8"))
        self.assertEqual({e["name"]: int(e["address"], 16) for e in js}, symbols._BY_NAME)

    def test_patch_constants_by_name(self):                              # the sym() helper, shown on ssj2_idle
        self.assertEqual(sym("idle_tick"), 0x08007570)
        self.assertEqual(sym_ptr("idle_tick"), ssj2_idle.VANILLA_TICK)
        self.assertEqual(ssj2_idle.VTABLES, (sym("vt_state0_idle"), sym("vt_state38")))
        self.assertEqual(ssj2_idle.LEFT_VANILLA, sym("vt_state22"))
        self.assertEqual(sym_rom("set_table"), 0x3B4E90)
        self.assertEqual(sym_ptr("decompress"), 0x03000000)                # IWRAM code is ARM: no Thumb bit
        with self.assertRaisesRegex(KeyError, "idle_tick"):
            sym("idle_tik")


if __name__ == "__main__":
    unittest.main()
