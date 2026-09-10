#!/usr/bin/env python3
"""Structural/language inspection of the downloaded Ge'ez source.

This script measures only. It does not translate or interpret the corpus.
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_INPUT = Path("BIBLIA/input/ETHIOPIAN_BIBLE/SOURCE/geez-complete.md")
DEFAULT_OUTPUT = Path("BIBLIA/input/ETHIOPIAN_BIBLE/STRUCTURAL_INSPECTION.json")
GEEZ_RE = re.compile(r"[\u1200-\u137F]")


def inspect(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    chars = Counter(text)
    geez_chars = sum(n for ch, n in chars.items() if GEEZ_RE.match(ch))
    letters = sum(n for ch, n in chars.items() if ch.isalpha())
    lines = text.splitlines()
    nonempty = [line for line in lines if line.strip()]
    return {
        "status": "MEDICION_REALIZADA",
        "file": str(path),
        "bytes": path.stat().st_size,
        "characters": len(text),
        "lines": len(lines),
        "nonempty_lines": len(nonempty),
        "geez_unicode_characters": geez_chars,
        "alphabetic_characters": letters,
        "geez_share_of_alphabetic_characters": (geez_chars / letters) if letters else 0,
        "contains_english_comparison_layer_marker": "English (compare)" in text,
        "contains_translation_heading": bool(re.search(r"^English|^Translation|^KJV|^NIV", text, re.I | re.M)),
        "interpretation": "NO REALIZADA"
    }


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    if not source.exists():
        raise SystemExit(f"ERROR: fuente no encontrada: {source}")
    result = inspect(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
