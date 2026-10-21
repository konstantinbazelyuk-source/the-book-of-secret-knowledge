#!/usr/bin/env python3
"""Reassemble the archived Kokoro Lumina Forest offline HTML from GitHub parts.

Usage: python RESTORE_LUMINA_FOREST.py
No external dependencies.
"""
from pathlib import Path
import hashlib

folder = Path(__file__).resolve().parent
stem = "Kokoro_Lumina_Forest_Offline_Alpha.html"
parts = [folder / f"{stem}.part{i:02d}" for i in range(1, 5)]
missing = [str(p) for p in parts if not p.exists()]
if missing:
    raise SystemExit("Missing segments: " + ", ".join(missing))
destination = folder / stem
if destination.exists():
    raise SystemExit(f"Refusing to overwrite existing file: {destination}")
with destination.open("wb") as out:
    for part in parts:
        with part.open("rb") as source:
            while True:
                block = source.read(1048576)
                if not block:
                    break
                out.write(block)
h = hashlib.sha256()
with destination.open("rb") as source:
    for block in iter(lambda: source.read(1048576), b""):
        h.update(block)
print(f"Wrote {destination.name} ({destination.stat().st_size} bytes)")
print("SHA-256 of published reassembled text:", h.hexdigest())
