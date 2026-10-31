r"""
symbols.py - Names for the LoG II USA functions, tables and RAM globals that docs\RE-BIBLE.md names.

Usage:   (from scripts\permanent) py -3 -I disasm\symbols.py [list | check | json]
         list   every symbol with its bible row tag (section, tags, label, source)
         check  every bible code address against scripts\permanent\disasm\data\codemap.json: function start, inside a function,
                vtable, pool, string or unclassified; and every "func" symbol against the function list
         json   write scripts\permanent\disasm\data\symbols.json (name, address, kind, bible) for Ghidra and other tools
API:     addr(name) -> GBA address; rom(name) -> file offset; ptr(name) -> the value code stores for a
         function (start + 1 for Thumb, start for ARM); name_of(addr) -> name or None; S.<name> -> address;
         bible_rows() -> [Row]; bible_tag(addr) -> "s14 #boot C OVW" or "";
         for_codemap(game) -> {"names", "tags", "functions", "ptr_tables"} (USA only; empty for others).
Rules:   A name here is a label for an address the bible already states; the bible row is the evidence.
         Kinds: func (a function start), table (ROM data), vtable (base-relative method table, ROM),
         ram (IWRAM or EWRAM global). Call sites and mid-function addresses stay in the bible only;
         listing.py shows them as comments. Patches use scripts\permanent\rom\re_sym.py (sym, sym_rom, sym_ptr),
         which loads this file. Adopted from scripts\one-time\2026-10-18-disasm-study\; this copy is the maintained one.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # scripts\permanent\disasm
ROOT = HERE.parents[2]                             # the LOG root
OUT_DIR = HERE / "data"                            # committed outputs (not the LOG data\ folder)
BIBLE = ROOT / "docs" / "RE-BIBLE.md"
ROM_BASE = 0x08000000
ARM_FUNCS = (0x080000C0, 0x0802369C)               # crt0 and the cpp_init veneer; IWRAM code is ARM too
IWRAM_CODE = (0x03000000, 0x03000E7C)              # crt0 copies rom:0x7FD6BC here (bible s14 #boot)

# ===== functions (start addresses; codemap.py checks each one is a start) =====
FUNCS = [
    # boot, scenes, frame loop, IRQ
    (0x080000C0, "crt0"), (0x08000158, "main"), (0x0802369C, "veneer_cpp_init"), (0x08021D74, "cpp_init"),
    (0x0801F248, "system_init"), (0x0801EDE0, "logo_scene"), (0x0801D378, "logo_scene2"),
    (0x0801ED3C, "intro_scene"), (0x0801F2CE, "scene_set"), (0x0801F294, "frame_loop"),
    (0x0801F2F4, "scene_push"), (0x08020D40, "vblank_wait"), (0x08020D26, "irq_init"),
    (0x0801F230, "vblank_callback"), (0x03000824, "irq_handler"), (0x080005A4, "title_enter"),
    (0x08000CD8, "file_select"), (0x08001960, "file_select_slots"), (0x08001A8A, "file_select_leader_pos"),
    (0x08004EA8, "field_update"), (0x08004EDC, "field_tick"), (0x08004CAC, "menu_buttons"),
    (0x0801EEFC, "input_read"), (0x0801EF64, "input_cheats"),
    # codec, VRAM
    (0x03000000, "decompress"), (0x0300024C, "bits_read"), (0x0300029C, "unpack_remap"),
    (0x03000958, "unpack_type1"), (0x080236A8, "veneer_decompress"), (0x0801F394, "frame_unpack"),
    (0x0801F3BA, "frame_unpack_remap"), (0x08021DF0, "memcpy_any"), (0x080067AC, "obj_vram_alloc"),
    (0x0800784C, "frame_vram_copy"),
    # objects and world
    (0x080068B8, "world_add"), (0x080068CA, "world_remove"), (0x08006942, "world_replace"),
    (0x08006AA6, "world_oam"), (0x08006AD8, "world_update"), (0x08006DA6, "world_broadcast"),
    (0x08006E0A, "world_query"), (0x08006E64, "world_count"), (0x08006F4A, "world_pause"),
    (0x08006FA4, "world_resume"), (0x080075A8, "sprite_ctor"), (0x080078E4, "mover_ctor"),
    (0x0800F80C, "combatant_ctor"), (0x080086D4, "player_ctor"), (0x080129B8, "player_fly_ctor"),
    (0x08019B30, "sprite_ctor_chain"), (0x0800D6DE, "npc_factory"), (0x0800B710, "interactive_factory"),
    (0x0800E77E, "enemy_factory"), (0x08008B14, "hud_ctor"), (0x080076EE, "obj_set_table"),
    (0x08007C70, "menu_sprite_ctor"), (0x08007CB6, "menu_sprite_state"),
    # sprites and animation states
    (0x08009324, "get_set"), (0x08009370, "find_actor_by_set"), (0x08007520, "walk_enter"),
    (0x08007532, "walk_tick"), (0x08007554, "idle_enter"), (0x08007570, "idle_tick"),
    (0x08007588, "stand22_enter"), (0x08007772, "frame_upload"), (0x08010760, "anim16_enter"),
    (0x08010774, "anim16_tick"), (0x080083C2, "hold_special_tick"),
    # player, states, combat
    (0x08007DE8, "button_a"), (0x08007F34, "idle_control"), (0x080082C8, "hurt_move"),
    (0x080085AC, "punch_hold_check"), (0x080085FC, "player_refresh"), (0x080086A2, "form_reapply"),
    (0x08008784, "player_take_damage"), (0x08008806, "player_apply_hit"), (0x080088BA, "player_set_state"),
    (0x08008944, "player_message"), (0x08008B88, "ability_cycle"), (0x08008BEE, "hud_draw"),
    (0x0800F910, "damage"), (0x0800E5B8, "enemy_message"), (0x0801AB2A, "enemy_ai_hit"),
    (0x08011D38, "powerup_enter"), (0x08011D4A, "powerup_tick"), (0x08012A04, "state_heap_set"),
    (0x08014D58, "transform"), (0x08014DE0, "ki_blast_enter"), (0x0801563C, "transform_end"),
    (0x080157AE, "revert_end"), (0x080169B8, "charged_ball_fire"),
    # forms
    (0x08017028, "form_base_tick"), (0x08017158, "form_rage_enter"), (0x08017174, "form_rage_leave"),
    (0x08017298, "form_super_leave"), (0x08017306, "form_ssj_tick"), (0x08017376, "form_ssj_enter"),
    (0x08017392, "form_ssj_leave"), (0x08017400, "form_namek_tick"), (0x0802609C, "form_namek_leave"),
    (0x080232E4, "form_objects_init"),
    # save, characters, levels
    (0x08003C24, "save_defaults"), (0x08003CA0, "level_up"), (0x08003E42, "flag_test"),
    (0x08003E5E, "flag_set"), (0x08003E74, "flag_clear"), (0x08003ED4, "appearance_revert"),
    (0x08003F06, "condition_eval"), (0x08003F9C, "slot_load"), (0x08003FEC, "slot_write"),
    (0x08004030, "save_game"), (0x0800415C, "visited_test"), (0x080041A6, "ext23_visited"),
    (0x08004214, "level_of"), (0x08004230, "level_of_record"), (0x08004276, "exp_add"),
    (0x080042BC, "appearance_of_set"), (0x08005C0A, "debug_level"), (0x08021454, "save_init"),
    (0x08021526, "slot_copy"), (0x0802153E, "adler32"), (0x08027F1C, "umod"), (0x080218E0, "eeprom_identify"),
    (0x08021ACC, "eeprom_read"), (0x08021CB0, "eeprom_write"), (0x08026440, "appearance_portrait"),
    (0x0802645C, "appearance_set"),
    # menus, status, text
    (0x08000C18, "menu_tick"), (0x0800273A, "menu_input"), (0x08002A5A, "menu_page_input"),
    (0x08003480, "char_menu_ctor"), (0x0800350A, "menu_page_count"), (0x08003520, "menu_page_abilities"),
    (0x08003684, "menu_page_hold"), (0x0800379C, "status_page"), (0x08003B44, "menu_page_draw"),
    (0x08003B72, "menu_page_hook"), (0x08010BCE, "party_screen"), (0x08011172, "switch_characters"),
    (0x08001AB8, "menu_party_sprites"), (0x08017A50, "area_map_ctor"), (0x08018540, "scouter_ctor"),
    (0x08019102, "scouter_match"), (0x0801F636, "text_draw"), (0x0801F702, "text_wrapped"),
    (0x08020EC2, "glyph_draw"), (0x08021188, "blit"), (0x0802130A, "fill_rect"), (0x0800BDCC, "portrait"),
    (0x080264A8, "always_visible"),
    # script VM and cutscenes
    (0x080092E4, "script_run"), (0x08008F44, "op_push_u8"), (0x08009466, "ext131_gain_str"),
    (0x08009478, "ext132_gain_pow"), (0x0800948A, "ext133_gain_end"), (0x080095E4, "ext21_item_count"),
    (0x080096CA, "ext76_item_dec"), (0x080096E8, "ext77_item_sub"), (0x08009740, "ext29_party_msg"),
    (0x0800975E, "ext30_party_msg"), (0x08009B5E, "ext42_palette_fx"), (0x08009BF8, "ext46_sound_start"),
    (0x08009C54, "ext47_sound_stop"), (0x08009C8A, "ext49_music"), (0x08009FC4, "ext57_set_state"),
    (0x0800A680, "set_leader"), (0x0800A784, "ext70_set_leader"), (0x0800A8EC, "ext73_appearance"),
    (0x0800A9B6, "ext79_party_join"), (0x0800A9DA, "ext91_party_leave"), (0x0800AA10, "ext80_bit1_set"),
    (0x0800AA34, "ext81_bit1_clear"), (0x0800AA58, "ext82_bit5_set"), (0x0800B19C, "scene_type0"),
    (0x0800B1E2, "dialog_box"), (0x0800B304, "scene_type2"), (0x0800B33E, "scene_type3"),
    (0x0800B396, "scene_type4"), (0x0800B428, "scene_handler0"), (0x0800B438, "scene_type1"),
    (0x0800B494, "scene_type5"), (0x0800B520, "scene_run"), (0x0800DCA8, "move_vector"),
    (0x0800DF1C, "ext31_move"), (0x0800E04C, "actor_queue"),
    # maps
    (0x0800C390, "map_load_core"), (0x0800C584, "map_load"), (0x0800C232, "region_warp"),
    (0x0800C2C2, "region_script"), (0x0800D7E0, "region_scene"), (0x0800D9C2, "region_warp2"),
    (0x0800D838, "trigger_a_press"), (0x0800D87E, "trigger_a_facing"), (0x0800DA68, "palette_copy"),
    (0x0800E0AC, "map_count"), (0x0800EB7C, "map_find"), (0x0800FA6C, "pickup_ctor"),
    (0x080106B2, "scene_owner"), (0x08010AC6, "save_point_factory"), (0x08005D6C, "collision_test"),
    (0x08006250, "regions_tick"), (0x08006366, "move_test_b"), (0x0800638C, "move_test_a"),
    # items
    (0x0800F3F0, "item_pickup"), (0x0800F45A, "item_str"), (0x0800F4C2, "item_pow"), (0x0800F52A, "item_end"),
    (0x0800F592, "item_hp"), (0x0800F638, "item_ep"), (0x0800F6E8, "item_senzu"),
    # sound, library
    (0x08020A4C, "music_play"), (0x08020AF4, "sound_init"), (0x08020BD8, "sound_update"),
    (0x0801FC22, "sound_stop"), (0x0801FC9C, "sound_start"), (0x0801F878, "assert_fail"),
    (0x08021D28, "call_via_r0"), (0x08021D2A, "call_via_r1"), (0x08021D2C, "call_via_r2"),
    (0x08021D2E, "call_via_r3"), (0x08021D30, "call_via_r4"), (0x08021D32, "call_via_r5"),
    (0x08021D34, "call_via_r6"), (0x08021D36, "call_via_r7"), (0x0802141C, "rand_n"), (0x0802142E, "rand16"),
]

# ===== ROM tables, vtables and RAM globals =====
DATA = [
    # (address, name, kind)
    (0x083B4E90, "set_table", "table"), (0x081D967C, "appearance_table", "table"),
    (0x081DA6C8, "obj_palette", "table"), (0x081D4F50, "menu_palette", "table"),
    (0x081D9900, "ability_table", "table"), (0x081D9548, "default_records", "table"),
    (0x081D9834, "exp_table", "table"), (0x081D95F0, "stat_gain_ranges", "table"),
    (0x083B5C00, "script_base_ops", "table"), (0x083B5D28, "script_ext_ops", "table"),
    (0x083B5C78, "script_globals", "table"), (0x083B5278, "state_slots", "table"),
    (0x083B5268, "player_state_base", "table"), (0x083B51C8, "hurt_vectors", "table"),
    (0x083EC84C, "scene_handlers", "table"), (0x083EC9D0, "portrait_block", "table"),
    (0x08409368, "map_table", "table"), (0x086ADE24, "item_table", "table"),
    (0x086DB2CC, "move_table", "table"), (0x080E15B0, "sfx_table", "table"),
    (0x081D4B2C, "music_table", "table"), (0x0814A8A4, "music_instruments", "table"),
    (0x0814AD60, "music_samples", "table"), (0x080E2840, "string_table", "table"),
    (0x08028724, "menu_font", "table"), (0x086F7E50, "globals_a", "table"), (0x081D952C, "globals_b", "table"),
    (0x087FBDAC, "system_table", "table"), (0x086D7B54, "hud_frame", "table"),
    (0x086DAE7C, "icon_z", "table"), (0x086DB07C, "icon_z_dim", "table"), (0x086F869C, "stat_bar_frame", "table"),
    (0x081D9638, "status_background", "table"), (0x086F6D8C, "visited_table", "table"),
    (0x081DA970, "obj_vram_allocator", "table"), (0x081DA978, "menu_sprite_states", "table"),
    (0x086D0DD0, "gray_table", "table"), (0x086D0ED0, "menu_dim_table", "table"),
    (0x08023588, "ctor_list", "table"),
    (0x08023884, "vt_field_scene", "vtable"), (0x08023B0C, "vt_file_select", "vtable"),
    (0x08023B3C, "vt_menu_base", "vtable"), (0x080248CC, "vt_char_menu", "vtable"),
    (0x08024004, "vt_form_base", "vtable"), (0x08024E4C, "vt_form_rage", "vtable"),
    (0x0802526C, "vt_form_super", "vtable"), (0x08024C58, "vt_form_ssj", "vtable"),
    (0x08024ABC, "vt_form_namek", "vtable"), (0x0802408C, "vt_hud", "vtable"),
    (0x08024A00, "vt_state_walk", "vtable"), (0x08024BA0, "vt_state38", "vtable"),
    (0x08024E84, "vt_mover", "vtable"), (0x08024FC4, "vt_palette_fx", "vtable"),
    (0x0802545C, "vt_scene_task", "vtable"), (0x08025564, "vt_combatant", "vtable"),
    (0x08025604, "vt_player", "vtable"), (0x080257D0, "vt_npc", "vtable"),
    (0x0802588C, "vt_state22", "vtable"), (0x08025A84, "vt_state0_idle", "vtable"),
    (0x08025B80, "vt_state9_powerup", "vtable"), (0x08025BAC, "vt_ext57_command", "vtable"),
    (0x08025C30, "vt_menu_sprite", "vtable"), (0x08025CCC, "vt_state51_ball", "vtable"),
    (0x08025D48, "vt_state34_ki", "vtable"), (0x08025D70, "vt_state_punch", "vtable"),
    (0x08025E20, "vt_state39_hold", "vtable"),
    (0x03000E1C, "scene_manager", "ram"), (0x03000E20, "vblank_count", "ram"), (0x03000E3C, "video", "ram"),
    (0x03000E90, "save_struct", "ram"), (0x03000FF4, "camera", "ram"), (0x03001090, "map_view", "ram"),
    (0x03001120, "world", "ram"), (0x03001D18, "suspended_list", "ram"), (0x03001FA8, "player_ptr", "ram"),
    (0x03001FB0, "script_regs", "ram"), (0x03001FC0, "sram_probe", "ram"), (0x03001FC1, "level_gains", "ram"),
    (0x03001FC4, "map_return", "ram"), (0x03001FE0, "regions", "ram"), (0x03002080, "map_info", "ram"),
    (0x030020F8, "actor_queue_obj", "ram"), (0x030021E0, "form_objects", "ram"), (0x0300229C, "input", "ram"),
    (0x030026BC, "sound", "ram"), (0x03003898, "eeprom_shadow_ptr", "ram"), (0x0300389C, "save_obj", "ram"),
    (0x03007FFC, "irq_vector", "ram"), (0x0203E000, "eeprom_shadow", "ram"),
]

# Pointer tables codemap.py reads as seeds: name -> (address, count, stride, word offsets, relative to)
PTR_TABLES = {
    "script_base_ops": (0x083B5C00, 30, 4, [0], "abs"),
    "script_ext_ops": (0x083B5D28, 145, 4, [0], "abs"),
    "scene_handlers": (0x083EC84C, 6, 4, [0], "abs"),
    "ability_table": (0x081D9900, 14, 16, [8, 12], "abs"),
    "item_table": (0x086ADE24, 50, 56, [0x30, 0x34], "abs"),
    "ctor_list": (0x08023588, 66, 4, [0], "self"),
}

_BY_NAME = {n: a for a, n in FUNCS} | {n: a for a, n, _ in DATA}
_BY_ADDR = {a: n for n, a in _BY_NAME.items()}
_KIND = {a: "func" for a, _ in FUNCS} | {a: k for a, _, k in DATA}


class _Names:
    def __getattr__(self, name):
        return addr(name)


S = _Names()


def addr(name: str) -> int:
    return _BY_NAME[name]


def rom(name: str) -> int:
    a = _BY_NAME[name]
    if not ROM_BASE <= a < 0x0A000000:
        raise ValueError(f"{name} is not a ROM address")
    return a - ROM_BASE


def name_of(a: int):
    return _BY_ADDR.get(a)


def mode_of(a: int) -> str:
    """ "A" (ARM) or "T" (Thumb) for a function start."""
    return "A" if a in ARM_FUNCS or IWRAM_CODE[0] <= a < IWRAM_CODE[1] else "T"


def ptr(name: str) -> int:
    a = _BY_NAME[name]
    if _KIND[a] != "func":
        raise ValueError(f"{name} is a {_KIND[a]}, not a function")
    return a | 1 if mode_of(a) == "T" else a


# ===== bible parser =====

class Row:
    def __init__(self, line_no, section, text, tags, label, src):
        self.line_no, self.section, self.text, self.tags, self.label, self.src = \
            line_no, section, text, tags, label, src

    def tag(self):
        return f"s{self.section} {self.tags} {self.label} {self.src}".strip()


_ROWS = None


def bible_rows() -> list:
    """Every 4-column fact row of the bible: | fact | tags | label | src |."""
    global _ROWS
    if _ROWS is None:
        _ROWS, section = [], ""
        for n, line in enumerate(BIBLE.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"## (\d+[a-z]?)\.", line)
            if m:
                section = m.group(1)
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
            if len(cells) >= 3 and cells[0] not in ("Fact", "Question", "Decision", "Search for") \
                    and not set(cells[0]) <= set("-"):
                _ROWS.append(Row(n, section, cells[0], cells[1], cells[2], cells[3] if len(cells) > 3 else ""))
    return _ROWS


def _mentions(row, a: int) -> bool:
    t = row.text.upper()
    forms = [f"@0X{a:08X}", f"@0X{a | 1:08X}", f"`0X{a:08X}`", f" 0X{a:08X}`", f"BL 0X{a:08X}"]
    if ROM_BASE <= a < 0x0A000000:
        forms.append(f"ROM:0X{a - ROM_BASE:X}`")
        forms.append(f"ROM:0X{a - ROM_BASE:X} ")
    return any(f in t for f in forms)


def bible_addresses(usa_only=True) -> dict:
    """{GBA address: [rows]} for every @0x... address in the bible (rows tagged game:bf or game:log2eu
    are other ROMs and are left out unless usa_only is False)."""
    out = {}
    for row in bible_rows():
        if usa_only and "game:" in row.tags:
            continue
        for m in re.finditer(r"@0x([0-9A-Fa-f]{8})", row.text):
            out.setdefault(int(m.group(1), 16), []).append(row)
    return out


def bible_tag(a: int) -> str:
    for row in bible_rows():
        if _mentions(row, a):
            return row.tag()
    return ""


def for_codemap(game: str) -> dict:
    if game != "usa":
        return {}
    return {"names": {a: n for a, n in _BY_ADDR.items()}, "tags": {a: bible_tag(a) for a in _BY_ADDR},
            "functions": {a: mode_of(a) for a, _ in FUNCS},
            "ptr_tables": PTR_TABLES}


# ===== commands =====

def _list():
    for a in sorted(_BY_ADDR):
        print(f"{a:#010x}  {_KIND[a]:6} {_BY_ADDR[a]:26} {bible_tag(a) or 'NOT IN BIBLE'}")
    print(f"{len(_BY_ADDR)} symbols: {sum(k == 'func' for k in _KIND.values())} func, "
          f"{sum(k == 'table' for k in _KIND.values())} table, {sum(k == 'vtable' for k in _KIND.values())} vtable, "
          f"{sum(k == 'ram' for k in _KIND.values())} ram")


def _check(path=OUT_DIR / "codemap.json"):
    import bisect
    cm = json.loads(Path(path).read_text(encoding="utf-8"))
    funcs = {int(k, 16): v for k, v in cm["functions"].items()}
    starts = sorted(funcs)
    vt = {int(k, 16): len(v) for k, v in list(cm["vtables"].items()) + list(cm["lists"].items())}
    pool = {p + k for p in cm["pool"] for k in range(4)}
    code_hi, (iw_src, iw_dst, iw_size) = cm["code_hi"], cm["iwram"]
    sys.path.insert(0, str(HERE))
    import codemap
    img = codemap.Image((ROOT / "data" / "roms" / codemap.GAMES["usa"]).read_bytes())
    counts, rows = {}, []
    for a, refs in sorted(bible_addresses().items()):
        if not (ROM_BASE <= a < code_hi or iw_dst <= a < iw_dst + iw_size):
            continue
        if a in funcs:
            k = "start"
        elif a & 1 and a - 1 in funcs:
            k = "start+1 (pointer)"
        elif a in vt or any(b <= a < b + 4 * n for b, n in vt.items()):
            k = "vtable or ctor list"
        elif a in pool:
            k = "pool word"
        else:
            i = bisect.bisect_right(starts, a) - 1
            s = starts[i] if i >= 0 else None
            if s is not None and a < s + max(funcs[s][1], funcs[s][2]):
                k = "inside"
                rows.append(f"  {a:#010x} inside {name_of(s) or hex(s)} +{a - s:#x}")
            elif iw_dst <= a < iw_dst + iw_size:
                k = "iwram data"
            elif codemap._cstring(img, a) or a - 1 in funcs:
                k = "string"
            else:
                k = "data in code region"
                rows.append(f"  {a:#010x} data in code region (bible line {refs[0].line_no})")
        counts[k] = counts.get(k, 0) + 1
    print("bible code-region addresses:", sum(counts.values()))
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:22} {v}")
    bad = [f"{a:#010x} {n}" for a, n in FUNCS if a not in funcs]
    print("func symbols that are not codemap starts:", len(bad), bad)
    named = sum(1 for a in funcs if a in _BY_ADDR)
    print(f"codemap functions named: {named} of {len(funcs)} ({100 * named / len(funcs):.1f} %)")
    print("\n".join(rows))


def _json():
    out = [{"name": n, "address": f"{a:#010x}", "kind": _KIND[a], "bible": bible_tag(a)} for a, n in sorted(_BY_ADDR.items())]
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "symbols.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"symbols.json: {len(out)} symbols")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    {"list": _list, "check": _check, "json": _json}[cmd](*sys.argv[2:])
