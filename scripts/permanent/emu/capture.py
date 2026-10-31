r"""
capture.py - Run one BizHawk capture job with no window, and return its artifacts.

Usage:   py -3.14 -P scripts\permanent\emu\capture.py <job.txt> [--run-dir DIR] [--dry-run]
Job:     one key or step a line, '#' starts a comment, forward slashes in every path.
         Keys (before the steps):  rom <path>   seed <path>   speed <percent>   timeout <seconds>
                                   name <label>
         Steps (in order):         wait <frames>            press <button> <frames>
                                   shot <name>              read <addr> <width> <label>
                                   savestate <path>         end
API:     parse_job(text) -> Job          job_steps_text(job) -> the steps file capture.lua reads
         check_rom(path) -> Path         rewrite_config(text, base_dir, speed, run_dir) -> text
         install_writes(after) -> [Path] run(job, run_dir) -> Result
         biz_saveram_name(rom) -> str    seed_saveram(seed, rom, base_dir, pad_to) -> Path
Rules:   the ROM must live under builds\. This tool never builds a ROM. It never writes inside the BizHawk
         install: the config copy's GBA "Base" entry is an absolute run folder, and every run checks the
         install for a file newer than its own marker.
Traps:   console.log does not reach stdout under --chromeless, so result.txt is the only channel.
         BizHawk names a SaveRAM file after the ROM with every '_' turned into a space.
         A read wider than INLINE_WIDTH goes to <label>.bin, because a result line holds a value, not a dump.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # -P omits the script folder

import log_paths  # noqa: E402

# ===== CONFIG =====
BIZHAWK = Path(r"C:\Users\josephgonzalez\Downloads\BizHawk-2.11.1-win-x64")
EMUHAWK = BIZHAWK / "EmuHawk.exe"
INSTALL_CONFIG = BIZHAWK / "config.ini"
CAPTURE_LUA = Path(__file__).resolve().parent / "capture.lua"
RUN_ROOT = log_paths.ROOT / "scratch" / "capture"
DEFAULT_TIMEOUT = 900
BUTTONS = ("A", "B", "Start", "Select", "Up", "Down", "Left", "Right", "L", "R")
STEP_WORDS = ("wait", "press", "shot", "read", "savestate", "end")
INLINE_WIDTH = 8                 # a read this wide or narrower goes in result.txt; wider goes to <label>.bin

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
        elif word == "savestate":
            if len(args) != 1:
                raise ValueError("savestate: one path")
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
