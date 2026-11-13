r"""
capture.py - Run one BizHawk capture job with no window, and return its artifacts.

Usage:   py -3.14 -P scripts\permanent\emu\capture.py <job.txt> [--run-dir DIR] [--dry-run]
Job:     one key or step a line, '#' starts a comment, forward slashes in every path.
         Keys (before the steps):  rom <path>   seed <path>   speed <percent>   timeout <seconds>
                                   name <label>
         Steps (in order):         wait <frames>            press <button> <frames>
                                   shot <name>              read <addr> <width> <label>
                                   savestate <path>         loadstate <path>
                                   write <addr> <width> <hex>
                                   end
API:     parse_job(text) -> Job          job_steps_text(job) -> the steps file capture.lua reads
         check_rom(path) -> Path         rewrite_config(text, base_dir, speed, run_dir) -> text
         install_writes(after) -> [Path] run(job, run_dir) -> Result
         biz_saveram_name(rom) -> str    seed_saveram(seed, rom, base_dir, pad_to) -> Path
         rom_crc(path) -> int            state_rom_crc(path) -> int or None
         check_savestates(job) -> [Path] check_loadstates(job, rom) -> [Path]
         check_writes(job) -> [(addr, width, hex)]
Rules:   the ROM must live under builds\. This tool never builds a ROM. It never writes inside the BizHawk
         install: the config copy's GBA "Base" entry is an absolute run folder, and every run checks the
         install for a file newer than its own marker.
         savestate refuses a target that exists; loadstate refuses a source that does not, a source that
         is not a BizHawk state, and a source made on another ROM. Both fail before BizHawk starts.
         write only reaches IWRAM or EWRAM, so a job can change a game value but never a register, the
         ROM or the BIOS. A run that writes is an ASSISTED run and must be reported as one.
Traps:   console.log does not reach stdout under --chromeless, so result.txt is the only channel.
         BizHawk names a SaveRAM file after the ROM with every '_' turned into a space.
         A read wider than INLINE_WIDTH goes to <label>.bin, because a result line holds a value, not a dump.
         savestate.load RETURNS false for a missing file and for an mGBA .ssN, and raises nothing
         (scratch\capture\probestate\state.txt), so an unchecked load runs the job from a cold boot.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import zipfile
import zlib
from compression import zstd
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # -P omits the script folder
import log_paths  # noqa: E402


# ===== CONFIG =====
BIZHAWK = log_paths.BIZHAWK
EMUHAWK = BIZHAWK / "EmuHawk.exe"
INSTALL_CONFIG = BIZHAWK / "config.ini"
CAPTURE_LUA = Path(__file__).resolve().parent / "capture.lua"
RUN_ROOT = log_paths.CAPTURE
DEFAULT_TIMEOUT = 900
BUTTONS = ("A", "B", "Start", "Select", "Up", "Down", "Left", "Right", "L", "R")
STEP_WORDS = ("wait", "press", "shot", "read", "write", "savestate", "loadstate", "end")
INLINE_WIDTH = 8                 # a read this wide or narrower goes in result.txt; wider goes to <label>.bin
WRITE_MAX = 8                    # a write carries its bytes on its own line, so it stays small
WRITE_AREAS = ((0x02000000, 0x40000), (0x03000000, 0x8000))    # EWRAM, IWRAM: the only writable areas
# A BizHawk .State is a zip. "Core.bin.zst" decompresses to the mGBA core state, and its u32 at
# STATE_CRC_OFF is zlib.crc32 of the whole ROM file. Measured 2026-11-07 on three states.
STATE_ZIP_MARK = "BizState 1.0"
STATE_CORE = "Core.bin.zst"
STATE_CRC_OFF = 12

@dataclass
class Job:
    rom: Path = None
    seed: Path = None
    speed: int = 100
    timeout: int = DEFAULT_TIMEOUT
    name: str = "capture"
    steps: list = field(default_factory=list)      # (word, args) in order

@dataclass
class Result:
    exit_code: int = None
    seconds: float = 0.0
    timed_out: bool = False
    run_dir: Path = None
    result_file: Path = None
    lines: list = field(default_factory=list)
    shots: list = field(default_factory=list)
    reads: dict = field(default_factory=dict)
    install_writes: list = field(default_factory=list)
    lua_ok: bool = False          # the Lua side wrote "# done ok=true"
    ended: bool = False           # the job's end step ran

    @property
    def good(self):
        return (self.exit_code == 0 and not self.timed_out and self.lua_ok and self.ended
                and not self.install_writes)

# ===== job parsing =====
def _int(word, text):
    try:
        return int(text, 0)
    except ValueError:
        raise ValueError(f"{word}: not a number: {text!r}")

def parse_job(text: str) -> Job:
    """Read the job text. Raises ValueError on any line the Lua side could not run."""
    job = Job()
    seen_end = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if seen_end:
            raise ValueError(f"line after end: {line!r}")
        word, *args = line.split()
        if word in ("rom", "seed"):
            if len(args) != 1:
                raise ValueError(f"{word}: one path, got {len(args)}")
            setattr(job, word, Path(args[0]))
        elif word in ("speed", "timeout"):
            if len(args) != 1:
                raise ValueError(f"{word}: one number, got {len(args)}")
            setattr(job, word, _int(word, args[0]))
        elif word == "name":
            if len(args) != 1:
                raise ValueError("name: one word")
            job.name = args[0]
        elif word == "wait":
            if len(args) != 1 or _int(word, args[0]) < 1:
                raise ValueError(f"wait: one frame count of 1 or more, got {args}")
            job.steps.append((word, [_int(word, args[0])]))
        elif word == "press":
            if len(args) != 2:
                raise ValueError("press: <button> <frames>")
            if args[0] not in BUTTONS:
                raise ValueError(f"press: unknown button {args[0]!r}; known: {', '.join(BUTTONS)}")
            if _int(word, args[1]) < 1:
                raise ValueError("press: frames of 1 or more")
            job.steps.append((word, [args[0], _int(word, args[1])]))
        elif word == "shot":
            if len(args) != 1 or not args[0].replace("_", "").replace("-", "").isalnum():
                raise ValueError(f"shot: one plain name, got {args}")
            job.steps.append((word, [args[0]]))
        elif word == "read":
            if len(args) != 3:
                raise ValueError("read: <addr> <width> <label>")
            addr, width = _int(word, args[0]), _int(word, args[1])
            if width < 1:
                raise ValueError("read: width of 1 or more")
            job.steps.append((word, [addr, width, args[2]]))
        elif word == "write":
            if len(args) != 3:
                raise ValueError("write: <addr> <width> <hex>")
            addr, width = _int(word, args[0]), _int(word, args[1])
            if not 1 <= width <= WRITE_MAX:
                raise ValueError(f"write: width of 1 to {WRITE_MAX}, got {width}")
            if len(args[2]) != 2 * width:
                raise ValueError(f"write: {2 * width} hex digits for {width} bytes, got {args[2]!r}")
            try:
                bytes.fromhex(args[2])
            except ValueError:
                raise ValueError(f"write: not hex: {args[2]!r}")
            job.steps.append((word, [addr, width, args[2].lower()]))
        elif word in ("savestate", "loadstate"):
            if len(args) != 1:
                raise ValueError(f"{word}: one path")
            job.steps.append((word, [args[0]]))
        elif word == "end":
            if args:
                raise ValueError("end: no arguments")
            job.steps.append((word, []))
            seen_end = True
        else:
            known = "rom, seed, speed, timeout, name, " + ", ".join(STEP_WORDS)
            raise ValueError(f"unknown word {word!r}; known: {known}")
    if job.rom is None:
        raise ValueError("the job names no rom")
    if not seen_end:
        raise ValueError("the job has no end step")
    if job.speed < 1:
        raise ValueError("speed: percent of 1 or more")
    return job

def job_steps_text(job: Job) -> str:
    """The steps file capture.lua reads: one step a line, decimal numbers, forward slashes."""
    out = []
    for word, args in job.steps:
        out.append(" ".join([word] + [str(a).replace("\\", "/") for a in args]))
    return "\n".join(out) + "\n"

# ===== guards =====
def check_rom(path, builds=None) -> Path:
    """The job may only name a .gba under builds\\. Raises ValueError otherwise."""
    rom = Path(path).resolve()
    root = Path(builds if builds else log_paths.BUILDS).resolve()
    if not rom.is_relative_to(root):
        raise ValueError(f"the ROM is outside builds: {rom}")
    if rom.suffix.lower() != ".gba":
        raise ValueError(f"the ROM is not a .gba file: {rom}")
    return rom

def check_savestates(job: Job) -> list:
    """Every savestate target, after refusing one that already exists. We never overwrite a state."""
    targets = [Path(args[0]) for word, args in job.steps if word == "savestate"]
    for t in targets:
        if t.exists():
            raise FileExistsError(f"the savestate target already exists: {t}")
    return targets

def rom_crc(path) -> int:
    """zlib.crc32 of the whole ROM file. This is the value a BizHawk state carries."""
    return zlib.crc32(Path(path).read_bytes())

def state_rom_crc(path):
    """The ROM crc32 inside a BizHawk state, or None when the file is not one we can read.

    An mGBA .ssN state is a PNG, not a zip, so it lands on the None path and the caller refuses it.
    """
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if STATE_ZIP_MARK not in names or STATE_CORE not in names:
                return None
            core = zstd.decompress(z.read(STATE_CORE))
    except (OSError, ValueError, zipfile.BadZipFile, zstd.ZstdError):
        return None
    if len(core) < STATE_CRC_OFF + 4:
        return None
    return int.from_bytes(core[STATE_CRC_OFF:STATE_CRC_OFF + 4], "little")

def check_loadstates(job: Job, rom=None) -> list:
    """Every loadstate source, after proving it exists, is a BizHawk state, and belongs to this ROM.

    savestate.load returns false and raises nothing, so every one of these faults would otherwise
    run the job from a cold boot and hand back a confident wrong picture.
    """
    sources = [Path(args[0]) for word, args in job.steps if word == "loadstate"]
    if not sources:
        return []
    rom = Path(rom if rom else job.rom)
    want = rom_crc(rom)
    for s in sources:
        if not s.exists():
            raise FileNotFoundError(f"the loadstate source does not exist: {s}")
        got = state_rom_crc(s)
        if got is None:
            raise ValueError(f"not a BizHawk state: {s}. BizHawk cannot load an mGBA .ssN state, "
                             f"and it reports the refusal as a false return, not as an error.")
        if got != want:
            raise ValueError(f"the state belongs to another ROM: {s} carries crc32 0x{got:08x} and "
                             f"{rom.name} is crc32 0x{want:08x}. A state loads only on the ROM "
                             f"that made it.")
    return sources

def check_writes(job: Job) -> list:
    """Every write step, after proving it lands wholly inside EWRAM or IWRAM.

    A write that reached a register, the ROM or the BIOS would be a different kind of tool, and a run
    that changes a game value is already an assisted run, so the reach stays as small as it can be.
    """
    out = []
    for word, args in job.steps:
        if word != "write":
            continue
        addr, width, data = args
        if not any(base <= addr and addr + width <= base + size for base, size in WRITE_AREAS):
            areas = ", ".join(f"0x{b:08X}-0x{b + s - 1:08X}" for b, s in WRITE_AREAS)
            raise ValueError(f"the write 0x{addr:08X} + {width} is outside EWRAM and IWRAM ({areas})")
        out.append((addr, width, data))
    return out

def install_writes(after: float, install=None) -> list:
    """Every file in the BizHawk install changed after the given time. An empty list is the pass."""
    hits = []
    for root, _dirs, names in os.walk(install if install else BIZHAWK):
        for name in names:
            p = Path(root) / name
            try:
                if p.stat().st_mtime > after:
                    hits.append(p)
            except OSError:
                pass
    return sorted(hits)

# ===== config copy =====
def rewrite_config(text: str, base_dir, speed: int, run_dir, throttled: bool = False) -> str:
    """Point the GBA Base path at base_dir and turn the throttle off. Every other key is kept.

    "Unthrottled" is the key that frees the speed. SpeedPercent and client.speedmode change nothing on
    their own: a run at SpeedPercent 100 with Unthrottled true still reaches about 1000 fps. throttled
    True keeps the throttle, for a real-time comparison run.
    """
    cfg = json.loads(text)
    base = str(Path(base_dir).resolve())
    found = False
    for entry in cfg.get("PathEntries", {}).get("Paths", []):
        if entry.get("System") == "GBA" and entry.get("Type") == "Base":
            entry["Path"] = base
            found = True
    if not found:
        raise ValueError("the config has no GBA Base path entry")
    cfg["PathEntries"]["LastRomPath"] = str(Path(run_dir).resolve())
    cfg["SpeedPercent"] = int(speed)
    cfg["ClockThrottle"] = bool(throttled)
    cfg["Unthrottled"] = not throttled
    cfg["VSyncThrottle"] = False
    cfg["SoundThrottle"] = False
    cfg["VSync"] = False
    cfg["SoundEnabled"] = False
    cfg["SoundEnabledNormal"] = False
    cfg["SkipLagFrame"] = False
    cfg["SaveWindowPosition"] = False
    cfg["RunInBackground"] = True
    cfg["SingleInstanceMode"] = False
    cfg["UpdateAutoCheckEnabled"] = False
    cfg["FirstBoot"] = False
    return json.dumps(cfg, indent=2)

def biz_saveram_name(rom) -> str:
    """BizHawk names the SaveRAM file after the ROM with every '_' turned into a space."""
    return Path(rom).stem.replace("_", " ") + ".SaveRAM"

def seed_saveram(seed, rom, base_dir, pad_to: int = 0) -> Path:
    """Copy our .sav into the run folder under the name BizHawk reads. pad_to 0 keeps the file size."""
    data = Path(seed).read_bytes()
    if pad_to and len(data) < pad_to:
        data = data + b"\xff" * (pad_to - len(data))
    out = Path(base_dir) / "SaveRAM" / biz_saveram_name(rom)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out

# ===== the run =====
def parse_result(path) -> tuple:
    """result.txt to (lines, shot names, {label: value or file}, lua ok, end step seen).

    A Lua fault is caught inside capture.lua, so BizHawk still exits 0. Only the "# done ok=" line and an
    "end" step prove the job really finished, and the caller must check both.
    """
    lines, shots, reads, ok, ended = [], [], {}, False, False
    path = Path(path)
    if not path.exists():
        return lines, shots, reads, ok, ended
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        lines.append(line)
        parts = line.split()
        if line.startswith("# done ok="):
            ok = line.strip().endswith("true")
        elif len(parts) >= 4 and parts[2] == "shot":
            shots.append(parts[3])
        elif len(parts) >= 6 and parts[2] == "read":
            reads[parts[3]] = parts[5]
        elif len(parts) == 3 and parts[2] == "end":
            ended = True
    return lines, shots, reads, ok, ended

def run(job: Job, run_dir=None, seed_pad: int = 0, throttled: bool = False) -> Result:
    """Build the run folder, launch BizHawk with a timeout, and collect the artifacts."""
    rom = check_rom(job.rom)
    check_loadstates(job, rom)
    check_writes(job)
    for target in check_savestates(job):
        target.parent.mkdir(parents=True, exist_ok=True)
    if run_dir:
        run_dir = Path(run_dir)
    else:
        run_dir = RUN_ROOT / f"{job.name}-{time.strftime('%Y%m%d-%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    base_dir = run_dir / "bizbase"
    for sub in ("SaveRAM", "State", "Screenshots"):
        (base_dir / sub).mkdir(parents=True, exist_ok=True)
    (run_dir / "shots").mkdir(exist_ok=True)

    if job.seed:
        seed_saveram(job.seed, rom, base_dir, pad_to=seed_pad)
    config = run_dir / "config.ini"
    config.write_text(rewrite_config(INSTALL_CONFIG.read_text(encoding="utf-8"),
                                     base_dir, job.speed, run_dir, throttled),
                      encoding="utf-8", newline="\n")
    (run_dir / "steps.txt").write_text(job_steps_text(job), encoding="utf-8", newline="\n")
    boot = run_dir / "run.lua"
    boot.write_text(
        'CAPTURE_DIR = "{}/"\nCAPTURE_SPEED = {}\ndofile("{}")\n'.format(
            str(run_dir.resolve()).replace("\\", "/"), job.speed,
            str(CAPTURE_LUA.resolve()).replace("\\", "/")),
        encoding="utf-8", newline="\n")

    marker = time.time() - 1
    cmd = [str(EMUHAWK), f"--config={config}", "--chromeless", f"--lua={boot}", str(rom)]
    (run_dir / "command.txt").write_text(" ".join(cmd) + "\n", encoding="utf-8", newline="\n")
    started = time.time()
    res = Result(run_dir=run_dir, result_file=run_dir / "result.txt")
    # Kill this process tree by its own pid. "/IM EmuHawk.exe" would also kill my own session and
    # any capture another task is running.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = proc.communicate(timeout=job.timeout)
        res.exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        res.timed_out = True
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        out, err = proc.communicate()
    (run_dir / "stdout.txt").write_text(out or "", encoding="utf-8", newline="\n")
    (run_dir / "stderr.txt").write_text(err or "", encoding="utf-8", newline="\n")
    res.seconds = time.time() - started
    res.lines, res.shots, res.reads, res.lua_ok, res.ended = parse_result(res.result_file)
    res.install_writes = install_writes(marker)
    return res

def main(argv=None):
    ap = argparse.ArgumentParser(description="Run one BizHawk capture job with no window.")
    ap.add_argument("job", help="the job file")
    ap.add_argument("--run-dir", default=None, help="the run folder (default scratch\\capture\\<name>-<stamp>)")
    ap.add_argument("--seed-pad", type=int, default=0, help="pad the seed SaveRAM with 0xFF to this size")
    ap.add_argument("--throttled", action="store_true",
                    help="keep BizHawk's throttle on, for a real-time comparison run")
    ap.add_argument("--dry-run", action="store_true", help="parse and check the job, launch nothing")
    args = ap.parse_args(argv)

    job = parse_job(Path(args.job).read_text(encoding="utf-8"))
    rom = check_rom(job.rom)
    if args.dry_run:
        check_loadstates(job, rom)
        check_savestates(job)
        check_writes(job)
        print(f"job ok: rom {rom}, {len(job.steps)} steps, speed {job.speed}, timeout {job.timeout}")
        return 0
    res = run(job, args.run_dir, seed_pad=args.seed_pad, throttled=args.throttled)
    print(f"exit {res.exit_code} timed_out {res.timed_out} lua_ok {res.lua_ok} ended {res.ended} "
          f"seconds {res.seconds:.1f}")
    print(f"run folder {res.run_dir}")
    for line in res.lines:
        print("  " + line)
    if res.install_writes:
        print("INSTALL WRITES (this is a fault):")
        for p in res.install_writes:
            print("  " + str(p))
    if not res.good:
        print("THE RUN DID NOT FINISH CLEANLY. Read result.txt before you trust any artifact.")
    return 0 if res.good else 1

if __name__ == "__main__":
    raise SystemExit(main())
