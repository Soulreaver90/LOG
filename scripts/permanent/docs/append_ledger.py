"""Append one prose line to a LOG ledger, read from a .txt so no escape pass touches it.

It matches the target file's OWN line ending. On 2026-11-06 a plain "\n" append put LF lines 34 to 40
into a CRLF queue.md, which left the file mixed. Reported counts cover the appended text only, so a
mixed file passed unnoticed until a whole-file scan caught it.
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
text = src.read_text(encoding="utf-8").rstrip("\n") + "\n"

existing = dst.read_bytes() if dst.is_file() else b""
crlf = existing.count(b"\r\n")
lf = existing.count(b"\n")
ending = "\r\n" if crlf and crlf == lf else "\n"       # CRLF only when EVERY line already uses it
if crlf and crlf != lf:
    print(f"  warning: {dst.name} is already mixed, {crlf} CRLF of {lf} lines; appending LF")

out = text.replace("\r\n", "\n").replace("\n", ending)
with dst.open("ab") as f:
    f.write(out.encode("utf-8"))

bad = [c for c in text if ord(c) < 32 and c != "\n"]
print(f"appended {len(out)} bytes to {dst} | ending {ending!r} | control chars: {len(bad)} | "
      f"dashes: {text.count(chr(8212)) + text.count(chr(8211))}")
