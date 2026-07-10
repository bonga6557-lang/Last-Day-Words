"""
Complete audit of game words vs KJV PDF and content quality rules.
Reads docs/words-catalog-export.json (from scripts/export-words-json.ts).
Outputs docs/WORD_AUDIT_REPORT.md and docs/word-audit-findings.json.
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KJV_PDF = Path(os.environ.get("KJV_PDF", str(Path.home() / "Downloads" / "kjv.pdf")))
CACHE = ROOT / "docs" / "_kjv_norm_cache.txt"
CATALOG = ROOT / "docs" / "words-catalog-export.json"
SEED_SQL = ROOT / "supabase" / "seed_content.sql"
REPORT = ROOT / "docs" / "WORD_AUDIT_REPORT.md"

# Intentional SDA study terms — not required to be contiguous KJV quotes
STUDY_TERMS = {
    "STRAIGHT TESTIMONY",
    "REJECTION OF TRUTH",
    "CLOSE OF PROBATION",
    "DEATH DECREE",
    "SECOND COMING",
    "EASTERN SKY",
    "PRE ADVENT JUDGMENT",
    "INVESTIGATIVE JUDGMENT",
    "BLOT OUT SINS",
    "CLEANSING OF SANCTUARY",
    "SUNDAY LAW",
    "MARK OF THE BEAST",
    "SEAL OF GOD",
    "LOUD CRY",
    "LATTER RAIN",
    "THREE ANGELS",
    "PREACHING THE GOSPEL",
    "SHAKING",
    "SIFTING",
    "SPIRITUALISM",
    "STRONG DELUSION",
    "ARMAGEDDON",
    "TRANSLATION",
    "HEALTH MESSAGE",
    "JACOBS TROUBLE",  # legacy form
    "TIME OF JACOBS TROUBLE",
    # Thematic labels (verse describes the idea; exact English may differ, e.g. Holy Ghost)
    "PERSECUTION",
    "PENTECOST",
    "HOLY SPIRIT",
    "RESURRECTION",
    "REFRESHING",
    "SHAKING",
    "SIFTING",
    "REMNANT",
    "NEW EARTH",
    "NEW JERUSALEM",
    "NO MORE DEATH",
    "FALSE PROPHETS",
    "SABBATH",
    "SEAL OF GOD",
    "MARK OF THE BEAST",
    "LOUD CRY",
    "LATTER RAIN",
    "THREE ANGELS",
    "PREACHING THE GOSPEL",
}


def normalize_search(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("'", " ")  # man's -> man s (PDF style)
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().upper()


def load_kjv() -> str:
    if CACHE.exists():
        return CACHE.read_text(encoding="utf-8")
    from pypdf import PdfReader

    pages = [(p.extract_text() or "") for p in PdfReader(str(KJV_PDF)).pages]
    n = normalize_search(" ".join(pages))
    CACHE.write_text(n, encoding="utf-8")
    return n


def in_kjv(phrase: str, kjv: str) -> bool:
    p = normalize_search(phrase)
    if p in kjv:
        return True
    p2 = re.sub(r"[^A-Z0-9\s]", " ", phrase.upper())
    p2 = re.sub(r"\s+", " ", p2).strip()
    if p2 in kjv:
        return True
    # PDF often splits possessives: man's -> MAN S, refiner's -> REFINER S
    for poss in (
        "MANS",
        "REFINERS",
        "JACOBS",
        "EAGLES",
        "LORDS",
        "GODS",
        "KINGS",
        "PRIESTS",
        "MENS",
        "WOMENS",
        "CHILDS",
    ):
        if poss in p2:
            alt = p2.replace(poss, poss[:-1] + " S")
            if alt in kjv:
                return True
    return False


def clue_leaks_regular(word: str, clue: str) -> list[str]:
    reasons = []
    wu, cu = word.upper(), clue.upper()
    if wu in cu:
        reasons.append("clue contains full answer")
        return reasons
    parts = [p for p in wu.split() if len(p) > 3]
    for i in range(len(parts) - 1):
        phrase = f"{parts[i]} {parts[i + 1]}"
        if phrase in cu:
            reasons.append(f"clue contains 2-word phrase '{phrase}'")
            break
    return reasons


def scripture_quality(scripture: str) -> list[str]:
    issues = []
    s = scripture.strip()
    if not s:
        issues.append("empty scripture")
        return issues
    if len(s) < 40:
        issues.append(f"scripture too short ({len(s)} chars)")
    if re.match(r"^[a-z]", s):
        issues.append("scripture starts with lowercase")
    if re.search(r"\d[A-Za-z]", s):
        issues.append("digit glued to letter")
    return issues


def parse_seed_words(sql_path: Path) -> dict[str, str]:
    if not sql_path.exists():
        return {}
    text = sql_path.read_text(encoding="utf-8")
    rows = re.findall(
        r"\(\s*'([^']+)'\s*,\s*'[^']+'\s*,\s*'((?:''|[^'])*)'",
        text,
    )
    out = {}
    for wid, word in rows:
        if re.match(r"^[a-z0-9-]+$", wid):
            out[wid] = word.replace("''", "'")
    return out


def main() -> None:
    if not CATALOG.exists():
        raise SystemExit("Missing catalog export. Run: npx tsx scripts/export-words-json.ts")

    chapters = json.loads(CATALOG.read_text(encoding="utf-8"))
    all_entries = []
    for ch in chapters:
        for w in ch["words"]:
            all_entries.append({**w, "chapterId": ch["id"], "chapterTitle": ch["title"]})

    print(f"Catalog: {len(chapters)} chapters, {len(all_entries)} words")
    print("Loading KJV...")
    kjv = load_kjv()

    findings: dict[str, list] = defaultdict(list)
    word_map: dict[str, list[str]] = defaultdict(list)

    for e in all_entries:
        word_map[normalize_search(e["word"])].append(e["id"])

    for word, ids in word_map.items():
        if len(ids) > 1:
            findings["duplicates"].append({"word": word, "ids": ids})

    for e in all_entries:
        wid, word = e["id"], e["word"]
        if word != word.upper():
            findings["casing"].append({"id": wid, "word": word})

        for reason in clue_leaks_regular(word, e["clue"] or ""):
            findings["clue_leaks"].append(
                {"id": wid, "word": word, "clue": e["clue"], "reason": reason}
            )

        for issue in scripture_quality(e["scripture"] or ""):
            findings["scripture_quality"].append(
                {
                    "id": wid,
                    "word": word,
                    "issue": issue,
                    "scripture_start": (e["scripture"] or "")[:90],
                }
            )

        w_norm = normalize_search(word)
        is_study = word.upper() in STUDY_TERMS or w_norm in {normalize_search(s) for s in STUDY_TERMS}
        if " " in w_norm or len(w_norm) >= 4:
            if not in_kjv(word, kjv):
                if is_study:
                    findings["study_terms_not_kjv_quote"].append(
                        {"id": wid, "word": word, "verse": e["verse"]}
                    )
                else:
                    findings["kjv_not_contiguous"].append(
                        {"id": wid, "word": word, "verse": e["verse"]}
                    )
            elif " " in w_norm:
                findings["kjv_ok_multi"].append({"id": wid, "word": word})

        scr = normalize_search(e["scripture"] or "")
        tokens = [
            t
            for t in w_norm.split()
            if len(t) > 2 and t not in {"THE", "AND", "FOR", "WITH", "FROM", "THAT", "THIS", "WAS", "HIS", "HER"}
        ]
        missing = [t for t in tokens if t not in scr]
        if tokens and len(missing) >= max(1, (len(tokens) + 1) // 2) and not is_study:
            findings["answer_not_in_scripture"].append(
                {
                    "id": wid,
                    "word": word,
                    "missing_tokens": missing,
                    "verse": e["verse"],
                }
            )

    seed_map = parse_seed_words(SEED_SQL)
    for e in all_entries:
        if e["id"] in seed_map and normalize_search(seed_map[e["id"]]) != normalize_search(e["word"]):
            findings["seed_mismatch"].append(
                {"id": e["id"], "client": e["word"], "seed": seed_map[e["id"]]}
            )

    meta = {
        "total_words": len(all_entries),
        "chapters": len(chapters),
        "multi_word": sum(1 for e in all_entries if " " in e["word"]),
        "kjv_ok_multi": len(findings["kjv_ok_multi"]),
        "study_terms": len(findings["study_terms_not_kjv_quote"]),
        "in_seed": sum(1 for e in all_entries if e["id"] in seed_map),
    }

    lines = [
        "# Word Catalog Audit Report",
        "",
        "**Generated by** `scripts/audit-all-words.py` (catalog from `export-words-json.ts`)",
        f"**KJV source:** `{KJV_PDF.name}`",
        f"**Total words:** {meta['total_words']} across {meta['chapters']} chapters",
        f"**Multi-word answers:** {meta['multi_word']}",
        f"**Multi-word contiguous in KJV:** {meta['kjv_ok_multi']}",
        f"**Intentional study terms (not KJV quotes):** {meta['study_terms']}",
        f"**Ids present in seed_content.sql:** {meta['in_seed']}",
        "",
        "## User trigger example (fixed)",
        "",
        "Previously: `MIDNIGHT CRY BEHOLD BRIDEGROOM` (missing article; not a KJV quote).",
        "Now: `BEHOLD THE BRIDEGROOM COMETH` (Matthew 25:6, contiguous KJV).",
        "Scripture field: `And at midnight there was a cry made, Behold, the bridegroom cometh; ...`",
        "",
        "## Summary counts",
        "",
        "| Category | Count | Severity |",
        "|---|---:|---|",
        f"| Duplicate word strings | {len(findings['duplicates'])} | high |",
        f"| Non-study answers not contiguous in KJV | {len(findings['kjv_not_contiguous'])} | **critical** |",
        f"| Study terms (allowed non-quotes) | {len(findings['study_terms_not_kjv_quote'])} | info |",
        f"| Scripture quality issues | {len(findings['scripture_quality'])} | high |",
        f"| Answer tokens missing from scripture field | {len(findings['answer_not_in_scripture'])} | medium |",
        f"| Regular clue leaks | {len(findings['clue_leaks'])} | medium |",
        f"| Seed vs client mismatch | {len(findings['seed_mismatch'])} | high |",
        f"| Casing issues | {len(findings['casing'])} | low |",
        "",
        "## Critical: non-study answers not contiguous in KJV",
        "",
    ]
    if not findings["kjv_not_contiguous"]:
        lines.append("**None.** All non-study multi/single answers resolve in the KJV corpus.")
    else:
        for item in sorted(findings["kjv_not_contiguous"], key=lambda x: x["id"]):
            lines.append(f"- **{item['id']}** `{item['word']}` ({item['verse']})")

    lines += ["", "## Study terms (not required to be exact KJV quotes)", ""]
    for item in sorted(findings["study_terms_not_kjv_quote"], key=lambda x: x["id"]):
        lines.append(f"- **{item['id']}** `{item['word']}` ({item['verse']})")

    lines += ["", "## Scripture quality issues", ""]
    if not findings["scripture_quality"]:
        lines.append("None.")
    else:
        for item in findings["scripture_quality"]:
            lines.append(f"- **{item['id']}**: {item['issue']} — `{item['scripture_start']}`")

    lines += ["", "## Regular clue leaks", ""]
    if not findings["clue_leaks"]:
        lines.append("None.")
    else:
        for item in findings["clue_leaks"]:
            lines.append(f"- **{item['id']}** `{item['word']}` — {item['reason']}")
            lines.append(f"  - {item['clue'][:140]}")

    lines += ["", "## Answer tokens sparse in scripture snippet", ""]
    if not findings["answer_not_in_scripture"]:
        lines.append("None.")
    else:
        for item in findings["answer_not_in_scripture"][:40]:
            lines.append(
                f"- **{item['id']}** `{item['word']}` missing {item['missing_tokens']} ({item['verse']})"
            )
        if len(findings["answer_not_in_scripture"]) > 40:
            lines.append(f"- … and {len(findings['answer_not_in_scripture']) - 40} more")

    lines += [
        "",
        "## Seed mismatches",
        "",
        "None." if not findings["seed_mismatch"] else "",
    ]
    for item in findings["seed_mismatch"]:
        lines.append(f"- **{item['id']}**: client=`{item['client']}` seed=`{item['seed']}`")

    lines += [
        "",
        "## How to re-run",
        "",
        "```bash",
        "npx tsx scripts/export-words-json.ts",
        "python scripts/audit-all-words.py",
        "npx tsx scripts/check-duplicate-words.ts",
        "npx tsx scripts/check-regular-clue-leaks.ts",
        "```",
        "",
        "## Fix tooling",
        "",
        "- `scripts/fix-word-accuracy.py` — rebuild expansion answers/scripture + core KJV fixes",
        "- `scripts/generate-seed.ts` — sync `supabase/seed_content.sql`",
        "",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    dump = {
        "meta": meta,
        "findings": {k: v for k, v in findings.items() if k != "kjv_ok_multi"},
    }
    (ROOT / "docs" / "word-audit-findings.json").write_text(
        json.dumps(dump, indent=2), encoding="utf-8"
    )
    print(f"Wrote {REPORT}")
    print("=== SUMMARY ===")
    for k in [
        "duplicates",
        "kjv_not_contiguous",
        "study_terms_not_kjv_quote",
        "scripture_quality",
        "answer_not_in_scripture",
        "clue_leaks",
        "seed_mismatch",
        "casing",
    ]:
        print(f"{k}: {len(findings[k])}")


if __name__ == "__main__":
    main()
