# Seeded Ghidra project (LoG II USA)

This folder holds the scripts that build the seeded Ghidra project and prove it. The project itself is in `scratch\ghidra\seeded\`. It is separate from the old `scratch\ghidra\LoG2.gpr`, which these scripts never touch.

## What the project holds

The seeding gives Ghidra our code map and names instead of its own guesses.

| Item | Value |
|---|---|
| Project | `scratch\ghidra\seeded\LoG2seeded.gpr`, program `log2_usa.gba` |
| ROM | `scratch\ghidra\seeded\log2_usa.gba`, a copy of the USA base ROM (SHA-1 `18e0715d...`). The copy exists because `analyzeHeadless.bat` fails on the parentheses in the original file name |
| Language | `ARM:LE:32:v4t`, compiler spec `default`, BinaryLoader, base `0x08000000` |
| Memory | `rom_code` 0x08000000-0x08028723 (read, execute), `rom_data` 0x08028724 to the end (read only, not executable), `iwram_code` 0x03000000-0x03000E7B (the crt0 copy of rom:0x7FD6BC, bible s14 #boot), `iwram` to 0x03007FFF, `ewram` 0x02000000-0x0203FFFF, `io` 0x04000000-0x040003FF (volatile) |
| Analyzers off | Function Start Pre Search, Function Start Search, Function Start Search After Code, Function Start Search After Data, Create Address Tables, Embedded Media, ARM Aggressive Instruction Finder, Aggressive Instruction Finder |
| Seeds | All 2,264 starts in `scripts\permanent\disasm\data\codemap.json`, each in its own mode (TMode 1 = Thumb, 0 = ARM) |
| Names | 226 function names and 89 labels (tables, vtables, RAM globals) from `scripts\permanent\disasm\data\symbols.json`. Each named function has a plate comment with its bible row tag |

> [!NOTE]
> `rom_data` is marked not executable, so no analyzer decodes sprite or map data as code. If a later study finds code past 0x08028723, re-run `scripts\permanent\disasm\codemap.py` first. `SeedSetup.java` splits the ROM at the new `code_hi`.

---

## Open it in the Ghidra GUI

1. Close any headless run on this project. A project open in one Ghidra process is locked for the others.
2. Start `%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC\ghidraRun.bat`.
3. Select **File > Open Project** and open `scratch\ghidra\seeded\LoG2seeded.gpr`.
4. In the project window, double-click `log2_usa.gba`. The CodeBrowser opens.
5. If Ghidra asks "Analyze now?", select **No**. The program is already analyzed. `SeedSetup.java` stores the analyzer settings in the program options, so a GUI analysis should use them too (LIKELY: not tested in the GUI). Check **Analysis > Auto Analyze** before you run one.
6. Press **G** and type a name (for example `idle_tick`) or an address. The Decompile window shows the function with our names.

> [!WARNING]
> A rerun of the seeding (below) uses `-overwrite`. It replaces the program and deletes any names, comments or types you added in the GUI. Keep GUI work in a different project, or do not rerun.

---

## Rerun the seeding

Run these PowerShell commands after a change to `codemap.json` or `symbols.json`. Run them from any folder. The first run takes about 1 minute.

```powershell
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'
$L  = 'the LOG root'
$gh = '%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat'
$gd = "$L\scripts\permanent\ghidra"
$d  = "$L\scripts\permanent\disasm\data"

# 1. Import, seed and analyze. Ends with seeded_funcs.txt.
& $gh "$L\scratch\ghidra\seeded" LoG2seeded -import "$L\scratch\ghidra\seeded\log2_usa.gba" -overwrite -loader BinaryLoader -loader-baseAddr 0x08000000 -loader-blockName rom -processor ARM:LE:32:v4t -cspec default -analysisTimeoutPerFile 3600 -scriptPath $gd -log "$gd\seeded_headless.log" -scriptlog "$gd\seeded_script.log" -preScript SeedSetup.java "$d\codemap.json" "$d\symbols.json" -postScript SeedReport.java "$gd\seeded_funcs.txt" *> "$gd\seeded_console.txt"

# 2. Count codemap starts found and false functions.
py -3 -I "$gd\seeded_compare.py"

# 3. Decompile by name into decomp\.
& $gh "$L\scratch\ghidra\seeded" LoG2seeded -process log2_usa.gba -noanalysis -readOnly -scriptPath $gd -log "$gd\decomp_headless.log" -scriptlog "$gd\decomp_script.log" -postScript Decomp.java "$gd\decomp" idle_tick scene_type1 get_set damage portrait *> "$gd\decomp_console.txt"
```

Expected output on 2026-10-19. Step 1 ends `seeded_script.log` with these lines:

```
SeedSetup.java> seeded: 2264 starts, 2264 functions, 0 failed, 226 named, 89 labels
SeedReport.java> functions 2289
SeedReport.java> error bookmarks {}
```

An address in `error bookmarks` is a bad instruction or a disassembly conflict: a candidate wrong codemap start or mode. Step 2 prints:

```
Ghidra functions: 2289; codemap starts: 2264
  codemap starts that are Ghidra functions, same mode: 2264
  codemap starts that are Ghidra functions, other mode: 0 []
  codemap starts with no Ghidra function: 0 []
  Ghidra only, inside a codemap body: 25 [...]
  Ghidra only, elsewhere in code: 0 []
  Ghidra only, outside code (false functions): 0 []
```

The 25 "inside a codemap body" functions are the ARM halves of Thumb `bx pc ; nop` veneers, at start + 4. They are real code. Ghidra makes them thunks, and codemap keeps them in the Thumb body.

> [!NOTE]
> The seeding forces every codemap start in, so "2264 same mode" shows that the starts survived analysis, not that Ghidra found them. The 0 Error bookmarks show that Ghidra's own disassembler decodes them without a conflict.

---

## Files

| File | What it does |
|---|---|
| `SeedSetup.java` | Pre-script: memory map, analyzer options, codemap starts with modes, names, labels and bible plate comments |
| `SeedReport.java` | Post-script: writes `seeded_funcs.txt` ("0xADDR SIZE THUMB\|ARM NAME") and counts Error bookmarks per block |
| `seeded_compare.py` | Compares `seeded_funcs.txt` with `codemap.json` |
| `Decomp.java` | Post-script: decompiles functions by name to `decomp\<name>.c`. Read-only ROM loads fold to constants |
| `AnalyzerList.java` | Probe: writes every analysis option name and value. Use it to check names after a Ghidra upgrade |
| `decomp\*.c` | The 5 proof decompiles |
| `FuncList.java`, `SeedEntry.java`, `ghidra_funcs.txt`, `headless.log`, `proj\` | The 2026-10-18 study run (unseeded auto-analysis), kept for comparison |
