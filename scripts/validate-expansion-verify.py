"""Check all verify substrings in build-word-expansion.py against kjv.pdf."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "build_word_expansion",
    ROOT / "scripts" / "build-word-expansion.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

KJV_PDF = Path(os.environ.get("KJV_PDF", str(Path.home() / "Downloads" / "kjv.pdf")))
pages = [(p.extract_text() or "") for p in PdfReader(str(KJV_PDF)).pages]

failed: list[tuple[str, str]] = []
for ch in mod.EXPANSION:
    for w in ch["words"]:
        wid = f"{ch['id']}-{w['id']}"
        needle = mod.normalize_pdf_text(w["verify"]).lower()
        if not any(needle in mod.normalize_pdf_text(text).lower() for text in pages):
            failed.append((wid, w["verify"]))

print(f"failed {len(failed)}")
for wid, verify in failed:
    print(f"{wid} => {verify!r}")
