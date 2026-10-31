#!/usr/bin/env bash
# package.sh BASE OUTNAME: diff snapshot BASE against the live trees into OUTNAME.diff (the review package).
set -euo pipefail
L="/c/Users/josephgonzalez/Documents/Projects/Workspace/LOG"; W="$L/scratch/review-snapshots"
tmp="$W/_live"; "$L/scripts/permanent/review/snap.sh" _live >/dev/null
out="$W/$2.diff"
{ echo "# Review package: snapshot $1 -> live"; echo; cd "$W"
  git -c core.autocrlf=false -c core.safecrlf=false diff --no-index --stat "$1" _live || true; echo
  git -c core.autocrlf=false -c core.safecrlf=false diff --no-index -U10 "$1" _live || true; } > "$out"
echo "$out"
