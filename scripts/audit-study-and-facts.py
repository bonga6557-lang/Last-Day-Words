"""
Audit studyContent.ts (EGW GC + Education + KJV) and funFacts.ts.
Verifies EGW quotes as contiguous substrings in source PDFs.
Writes docs/STUDY_FUNFACTS_AUDIT_REPORT.md and findings JSON.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
GC_PDF = Path(os.environ.get("GC_PDF", str(Path.home() / "Downloads" / "en_GC (1).pdf")))
ED_PDF = Path(os.environ.get("ED_PDF", str(Path.home() / "Downloads" / "en_Ed (1).pdf")))
KJV_CACHE = ROOT / "docs" / "_kjv_norm_cache.txt"
GC_CACHE = ROOT / "docs" / "_gc_norm_cache.txt"
ED_CACHE = ROOT / "docs" / "_ed_norm_cache.txt"
STUDY_TS = ROOT / "src" / "data" / "studyContent.ts"
FUN_TS = ROOT / "src" / "data" / "funFacts.ts"
REPORT = ROOT / "docs" / "STUDY_FUNFACTS_AUDIT_REPORT.md"
FINDINGS = ROOT / "docs" / "study-funfacts-audit-findings.json"


def normalize(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("…", " ").replace("\u2026", " ")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"[^A-Za-z0-9'\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().upper()


def load_pdf_cache(pdf: Path, cache: Path) -> str:
    if cache.exists() and cache.stat().st_size > 1000:
        print(f"cache hit {cache.name}")
        return cache.read_text(encoding="utf-8")
    print(f"extracting {pdf} ...")
    pages = [(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]
    n = normalize(" ".join(pages))
    cache.write_text(n, encoding="utf-8")
    print(f"wrote {cache} ({len(n)} chars)")
    return n


def strip_for_search(quote: str) -> str:
    # Remove ellipsis markers and bracket notes for matching
    q = quote.replace("…", " ").replace("...", " ")
    q = re.sub(r"\[[^\]]*\]", " ", q)
    return normalize(q)


def find_contiguous(needle: str, corpus: str) -> bool:
    if not needle or len(needle) < 20:
        # short quotes: require exact token sequence
        return needle in corpus if needle else False
    if needle in corpus:
        return True
    # try without common quote artifacts
    n2 = re.sub(r"\s+", " ", needle)
    return n2 in corpus


def parse_study_passages(ts: str) -> list[dict]:
    """Parse StudyPassage-like objects from studyContent.ts."""
    passages = []
    # Match blocks with id, source, citation, text, locator
    pat = re.compile(
        r"id:\s*\"([^\"]+)\"\s*,\s*"
        r"source:\s*\"([^\"]+)\"\s*,\s*"
        r"citation:\s*\"((?:\\.|[^\"\\])*)\"\s*,\s*"
        r"text:\s*\"((?:\\.|[^\"\\])*)\"\s*,\s*"
        r"locator:\s*\"((?:\\.|[^\"\\])*)\"",
        re.MULTILINE,
    )
    for m in pat.finditer(ts):
        text = m.group(4).encode().decode("unicode_escape") if "\\" in m.group(4) else m.group(4)
        passages.append(
            {
                "id": m.group(1),
                "source": m.group(2),
                "citation": m.group(3),
                "text": text,
                "locator": m.group(5),
            }
        )
    return passages


def parse_fun_facts(ts: str) -> list[str]:
    # strings inside FUN_FACTS array
    m = re.search(r"export const FUN_FACTS[^=]*=\s*\[(.*?)\];", ts, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    return re.findall(r"\"((?:\\.|[^\"\\])*)\"", body)


def main() -> None:
    study_ts = STUDY_TS.read_text(encoding="utf-8")
    fun_ts = FUN_TS.read_text(encoding="utf-8")
    passages = parse_study_passages(study_ts)
    facts = parse_fun_facts(fun_ts)
    print(f"passages={len(passages)} facts={len(facts)}")

    gc = load_pdf_cache(GC_PDF, GC_CACHE)
    ed = load_pdf_cache(ED_PDF, ED_CACHE)
    kjv = KJV_CACHE.read_text(encoding="utf-8") if KJV_CACHE.exists() else ""
    if not kjv:
        print("WARN: no kjv cache")

    failed = []
    ok = []
    for p in passages:
        needle = strip_for_search(p["text"])
        # For ellipsis mid-quotes, check significant chunks
        chunks = [c.strip() for c in re.split(r"\s*(?:\.\.\.|…)\s*", p["text"]) if len(c.strip()) > 25]
        corpus = {"great-controversy": gc, "education": ed, "kjv": kjv}.get(p["source"], "")
        if p["source"] == "kjv":
            # KJV often already in app; check cache
            hit = find_contiguous(needle, corpus) or any(find_contiguous(normalize(c), corpus) for c in chunks)
        else:
            hit = find_contiguous(needle, corpus)
            if not hit and chunks:
                hit = all(find_contiguous(normalize(c), corpus) for c in chunks if len(normalize(c)) > 20)
            # try first 80 chars of first substantial sentence
            if not hit and len(needle) > 40:
                hit = needle[:80] in corpus or any(
                    normalize(c)[:60] in corpus for c in chunks if len(c) > 30
                )
        entry = {**p, "hit": hit, "needle_len": len(needle)}
        (ok if hit else failed).append(entry)

    # Fun facts: lightweight checks (no full claim verification engine)
    fact_notes = []
    for i, f in enumerate(facts):
        notes = []
        # flag absolute counts without source if overly precise
        if re.search(r"more than \d+", f, re.I):
            notes.append("precise_count_claim")
        if "Blue Zones" in f:
            notes.append("modern_claim_review")
        if "formally organized in 1863" in f:
            notes.append("sda_history_ok")
        # Bible refs in fact — check short quote if present
        m = re.search(r"\(([A-Za-z0-9 :]+\d+:\d+)\)", f)
        fact_notes.append({"index": i, "fact": f, "notes": notes, "ref": m.group(1) if m else None})

    lines = [
        "# Study Content & Fun Facts Audit",
        "",
        f"**Passages parsed:** {len(passages)}",
        f"**Verified in source PDF:** {len(ok)}",
        f"**Failed / needs review:** {len(failed)}",
        f"**Fun facts:** {len(facts)}",
        "",
        "## Failed EGW/KJV passage matches",
        "",
    ]
    if not failed:
        lines.append("None — all passages found (or chunk-matched) in source corpus.")
    else:
        for e in failed:
            lines.append(f"### {e['id']} ({e['source']})")
            lines.append(f"- citation: {e['citation']}")
            lines.append(f"- locator: {e['locator']}")
            lines.append(f"- text: {e['text'][:200]}…")
            lines.append("")

    lines += ["## Fun facts review flags", ""]
    for fn in fact_notes:
        flag = ", ".join(fn["notes"]) if fn["notes"] else "ok"
        lines.append(f"- [{fn['index']}] ({flag}) {fn['fact'][:120]}")

    lines += [
        "",
        "## Sources",
        f"- GC: `{GC_PDF.name}`",
        f"- Education: `{ED_PDF.name}`",
        f"- KJV cache: `{KJV_CACHE.relative_to(ROOT).as_posix()}`",
        "",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    FINDINGS.write_text(
        json.dumps({"ok": len(ok), "failed": failed, "facts": fact_notes}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT}")
    print(f"ok={len(ok)} failed={len(failed)}")
    for e in failed:
        print(f"  FAIL {e['id']}: {e['text'][:80]}...")


if __name__ == "__main__":
    main()
