#!/usr/bin/env bash
# snap.sh NAME: copy the tracked trees (scripts/permanent, docs) to scratch/review-snapshots/NAME, for review diffs without git.
set -euo pipefail
L="/c/Users/josephgonzalez/Documents/Projects/Workspace/LOG"; W="$L/scratch/review-snapshots"
rm -rf "$W/$1"; mkdir -p "$W/$1"
cp -r "$L/scripts/permanent" "$W/$1/permanent"; cp -r "$L/docs" "$W/$1/docs"
find "$W/$1" -name __pycache__ -type d -prune -exec rm -rf {} +
echo "snapshot $1"
