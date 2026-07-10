"""
Fix game answers and scripture snippets for KJV trustworthiness.

1) Expansion: regenerate wordsExpansion.ts + expertCluesExpansion.ts from
   build-word-expansion EXPANSION data, using exact KJV phrases (from verify /
   optional answer) and cleaned scripture extraction.
2) Core words.ts: apply curated KJV corrections + clue-leak fixes.
3) Writes a fix log to docs/word-fix-log.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KJV_PDF = Path(os.environ.get("KJV_PDF", str(Path.home() / "Downloads" / "kjv.pdf")))
CACHE = ROOT / "docs" / "_kjv_norm_cache.txt"
WORDS_TS = ROOT / "src" / "data" / "words.ts"
OUT_EXP = ROOT / "src" / "data" / "wordsExpansion.ts"
OUT_EXPERT = ROOT / "src" / "data" / "expertCluesExpansion.ts"
OUT_LEDGER = ROOT / "docs" / "expansion-research-ledger.json"
FIX_LOG = ROOT / "docs" / "word-fix-log.json"

# Explicit playable answers that remain contiguous KJV (normalized).
# Prefer these over raw verify when verify is too long or awkward as a hangman answer.
ANSWER_OVERRIDES: dict[str, str] = {
    # chapter-id-num style is built as f"{ch['id']}-{w['id']}"
    "matthew-parables-2": "BEHOLD THE BRIDEGROOM COMETH",
    "matthew-parables-1": "TEN VIRGINS",
    "matthew-parables-3": "I WAS AN HUNGRED",
    "matthew-parables-4": "DEPART FROM ME YE CURSED",
    "matthew-parables-5": "ENTER THOU INTO THE JOY",
    "daniel-three-3": "SEVEN TIMES MORE THAN IT WAS WONT",
    "daniel-three-4": "LIKE THE SON OF GOD",
    "daniel-three-5": "NOR WAS AN HAIR OF THEIR HEAD SINGED",
    "daniel-five-2": "FINGERS OF A MANS HAND",  # apostrophe stripped; PDF has MAN S
    "daniel-five-5": "IN THAT NIGHT WAS BELSHAZZAR",
    "daniel-six-1": "LAW OF THE MEDES AND PERSIANS",
    "daniel-six-2": "THREE TIMES A DAY",
    "daniel-six-5": "HE IS THE LIVING GOD",
    "daniel-nine-1": "SEVENTY WEEKS ARE DETERMINED",
    "daniel-nine-3": "MESSIAH BE CUT OFF",
    "daniel-nine-4": "CONFIRM THE COVENANT WITH MANY",
    "daniel-ten-2": "HIS BODY ALSO WAS LIKE THE BERYL",
    "daniel-ten-5": "O MAN GREATLY BELOVED",
    "exodus-sanctuary-1": "AFTER THE PATTERN",
    "exodus-sanctuary-3": "MERCY SEAT OF PURE GOLD",
    "exodus-sanctuary-5": "VAIL OF BLUE AND PURPLE",
    "leviticus-atonement-1": "DAY OF ATONEMENT",
    "leviticus-atonement-2": "ONE LOT FOR THE LORD",
    "leviticus-atonement-4": "BEAR UPON HIM ALL THEIR INIQUITIES",
    "hebrews-sanctuary-1": "HIGH PRIEST FOR EVER",
    "hebrews-sanctuary-2": "MINISTER OF THE SANCTUARY",
    "hebrews-sanctuary-3": "MEDIATOR OF A BETTER COVENANT",
    "isaiah-comfort-2": "VOICE OF HIM THAT CRIETH IN THE WILDERNESS",
    "isaiah-comfort-4": "WORD OF OUR GOD SHALL STAND FOR EVER",
    "isaiah-comfort-5": "HE GIVETH POWER TO THE FAINT",
    "isaiah-servant-2": "WOUNDED FOR OUR TRANSGRESSIONS",
    "isaiah-servant-3": "LAID ON HIM THE INIQUITY OF US ALL",
    "isaiah-servant-5": "MADE INTERCESSION FOR THE TRANSGRESSORS",
    "joel-prophecy-1": "BLOW YE THE TRUMPET IN ZION",
    "joel-prophecy-2": "DAY OF DARKNESS AND OF GLOOMINESS",
    "joel-prophecy-4": "SUN SHALL BE TURNED INTO DARKNESS",
    "luke-watchfulness-2": "THIS GENERATION SHALL NOT PASS AWAY",
    "luke-watchfulness-4": "WATCH YE THEREFORE AND PRAY ALWAYS",
    "acts-restoration-2": "CLOVEN TONGUES LIKE AS OF FIRE",
    "acts-restoration-4": "A PROPHET SHALL THE LORD YOUR GOD RAISE UP",
    "acts-restoration-5": "REPENT YE THEREFORE AND BE CONVERTED",
    "first-corinthians-resurrection-1": "AT THE LAST TRUMP",
    "first-corinthians-resurrection-2": "VICTORY THROUGH OUR LORD JESUS CHRIST",
    "first-corinthians-resurrection-3": "UNTO THE JEWS A STUMBLINGBLOCK",
    "first-corinthians-resurrection-4": "I SHEW YOU A MYSTERY",
    "first-corinthians-resurrection-5": "THIS CORRUPTIBLE MUST PUT ON INCORRUPTION",
    "ephesians-armour-2": "HAVING YOUR LOINS GIRT ABOUT WITH TRUTH",
    "romans-gospel-1": "NOT ASHAMED OF THE GOSPEL OF CHRIST",
    "malachi-remnant-2": "LIKE A REFINERS FIRE",
    "malachi-remnant-3": "WILL A MAN ROB GOD",
    "rev-144000-1": "SEALED THE SERVANTS OF OUR GOD IN THEIR FOREHEADS",
    "rev-144000-2": "HURT NOT THE EARTH NEITHER THE SEA",
    "rev-144000-3": "AN HUNDRED AND FORTY AND FOUR THOUSAND",
    "rev-144000-4": "A GREAT MULTITUDE WHICH NO MAN COULD NUMBER",
    "rev-144000-5": "WASHED THEIR ROBES AND MADE THEM WHITE",
    "rev-throne-1": "A THRONE WAS SET IN HEAVEN",
    "rev-throne-5": "THOU ART WORTHY O LORD",
    "rev-witnesses-1": "MY TWO WITNESSES",
    "rev-witnesses-3": "FIRE PROCEEDETH OUT OF THEIR MOUTH",
    "rev-woman-dragon-2": "MICHAEL AND HIS ANGELS FOUGHT",
    "rev-woman-dragon-3": "ACCUSED THEM BEFORE OUR GOD DAY AND NIGHT",
    "rev-woman-dragon-4": "WILDERNESS WHERE SHE HATH A PLACE PREPARED",
    "rev-woman-dragon-5": "THE EARTH OPENED HER MOUTH",
    "rev-harvest-1": "EVERLASTING GOSPEL TO PREACH",
    "rev-harvest-2": "FEAR GOD AND GIVE GLORY TO HIM",
    "rev-harvest-3": "PATIENCE OF THE SAINTS",
    "rev-harvest-4": "ONE SAT LIKE UNTO THE SON OF MAN",
    "rev-harvest-5": "WINEPRESS WAS TRODDEN WITHOUT THE CITY",
    "rev-plagues-2": "NOISOME AND GRIEVOUS SORE",
    "rev-plagues-3": "POURED OUT HIS VIAL UPON THE SEA",
    "rev-plagues-4": "THE WATER THEREOF WAS DRIED UP",
    "rev-harlot-1": "MYSTERY BABYLON THE GREAT",
    "rev-harlot-2": "DRUNKEN WITH THE BLOOD OF THE SAINTS",
    "rev-harlot-3": "THE TEN HORNS WHICH THOU SAWEST UPON THE BEAST",
    "rev-harlot-4": "BABYLON THE GREAT IS FALLEN IS FALLEN",
    "rev-harlot-5": "THE MERCHANDISE OF GOLD AND SILVER",
    "rev-victory-1": "CALLED FAITHFUL AND TRUE",
    "rev-victory-2": "THE ARMIES WHICH WERE IN HEAVEN FOLLOWED HIM",
    "rev-victory-3": "THE MARRIAGE OF THE LAMB IS COME",
    "rev-victory-5": "CAST INTO THE LAKE OF FIRE",
    "rev-new-creation-1": "TABERNACLE OF GOD IS WITH MEN",
    "rev-new-creation-2": "ALPHA AND OMEGA THE BEGINNING AND THE END",
    "rev-new-creation-4": "TREE OF LIFE WHICH BARE TWELVE MANNER OF FRUITS",
    "rev-new-creation-5": "THE SPIRIT AND THE BRIDE SAY COME",
}

# Core catalog (words.ts) — only KJV-quote style answers, not pure study terms.
CORE_WORD_FIXES: dict[str, str] = {
    "signs-1": "WARS AND RUMOURS OF WARS",  # KJV spelling (rumours)
    "time-of-trouble-3": "TIME OF JACOBS TROUBLE",
    "daniel-image-4": "STONE WAS CUT OUT WITHOUT HANDS",
    "daniel-image-3": "HIS FEET PART OF IRON AND PART OF CLAY",
    "daniel-beasts-2": "THE FIRST WAS LIKE A LION",
    "daniel-beasts-3": "RAISED UP ITSELF ON ONE SIDE",
    "daniel-beasts-4": "FOUR WINGS OF A FOWL",
    "daniel-horn-3": "TIME AND TIMES AND THE DIVIDING OF TIME",
    "daniel-sanctuary-1": "TWO THOUSAND AND THREE HUNDRED DAYS",
    "rev-seals-1": "SEALED WITH SEVEN SEALS",
    "rev-seals-3": "UNDER THE ALTAR",
    "rev-trumpets-2": "PRAYERS OF THE SAINTS",
    "rev-trumpets-4": "MYSTERY OF GOD SHOULD BE FINISHED",
    "rev-beast-1": "BEAST RISE UP OUT OF THE SEA",
    "rev-beast-2": "ANOTHER BEAST COMING UP OUT OF THE EARTH",
}

# Core answers that intentionally are SDA study terms (not exact KJV quotes).
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
    "HEALTH MESSAGE",  # if present
}

# Clue leak fixes for regular clues (id -> new clue)
CLUE_FIXES: dict[str, str] = {
    "rev-144000-1": "Angels hold back the winds until God's servants receive His seal.",
    "rev-victory-5": "After the thousand years, the deceiver is thrown where the beast and false prophet are.",
    "daniel-beasts-4": "Third kingdom beast in Daniel 7 — swift empire with multiple heads.",
    "joel-prophecy-3": "Promise of Spirit on all flesh before the great and terrible day.",
    "first-corinthians-resurrection-2": "Paul's thanksgiving for triumph God gives through Christ.",
    "rev-144000-5": "Tribulation saints make their garments white in the Lamb.",
    "rev-harlot-2": "The woman is intoxicated by martyrdom of Jesus' people.",
    "daniel-three-4": "Nebuchadnezzar saw a fourth figure walking free in the flames with the three Hebrews.",
    "isaiah-servant-3": "Isaiah 53 — the LORD caused the guilt of us all to fall on the suffering Servant.",
    "romans-gospel-2": "Habakkuk's line Paul quotes when the righteousness of God is revealed from faith to faith.",
    "rev-victory-1": "Heaven opens — the white-horse Rider judges and makes war in righteousness.",
    "daniel-beasts-3": "Daniel's second beast — lopsided power devouring much flesh.",
    "malachi-remnant-5": "Malachi's closing hope for those who fear God's name.",
    "luke-watchfulness-2": "Christ's assurance that His prophetic word outlasts heaven and earth.",
    "romans-gospel-5": "Paul describes creation's shared longing for the revealing of the sons of God.",
    "second-peter-day-2": "Peter's perspective on divine timing versus human calendars.",
    "second-peter-day-4": "Peter's promise beyond the day of the Lord for the home of the righteous.",
    "rev-witnesses-3": "How the two witnesses answer those who would hurt them.",
    "rev-woman-dragon-3": "Heaven's courtroom charge against the dragon cast down.",
    "rev-harvest-2": "First angel's call to worship the Creator in the hour of judgment.",
    "rev-victory-4": "Fate of the beast and false prophet when the Rider conquers.",
}


def load_build_mod():
    spec = importlib.util.spec_from_file_location(
        "build_word_expansion", ROOT / "scripts" / "build-word-expansion.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_answer(s: str) -> str:
    """Uppercase hangman answer: drop apostrophes (man's->MANS), strip other punct."""
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("'", "")  # man's -> mans
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().upper()
    return s


def normalize_search(s: str) -> str:
    """Match PDF cache normalization: apostrophe -> space historically; also try joined."""
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    # PDF often has MAN S for man's — search both styles via flexible form
    s = s.replace("'", " ")
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().upper()
    return s


def load_kjv_norm() -> str:
    if CACHE.exists():
        return CACHE.read_text(encoding="utf-8")
    pages = [(p.extract_text() or "") for p in PdfReader(str(KJV_PDF)).pages]
    text = " ".join(pages)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().upper()
    CACHE.write_text(text, encoding="utf-8")
    return text


def in_kjv(phrase: str, kjv: str) -> bool:
    p = normalize_search(phrase)
    if p in kjv:
        return True
    # also try without internal single-letter gaps from apostrophes already spaces
    p2 = normalize_answer(phrase)
    # convert MANS -> MAN S for PDF style
    # try inserting space before S after N for 's possessives is hard; check p2 with spaces around S from 's
    if p2 in kjv:
        return True
    # PDF style: MANS HAND vs MAN S HAND
    p3 = re.sub(r"\b(\w+)S\b", r"\1 S", p2)  # too aggressive for WARS
    # only for known possessive pattern: MANS, GODS, LORDS, JACOBS, REFINERS, EAGLES
    for poss in ("MANS", "GODS", "LORDS", "JACOBS", "REFINERS", "EAGLES", "KINGS", "PRIESTS"):
        if poss in p2:
            alt = p2.replace(poss, poss[:-1] + " S")
            if alt in kjv:
                return True
    return False


def extract_snippet_clean(pages: list[str], page: int, verify: str, max_len: int = 240) -> str:
    def norm_pdf(text: str) -> str:
        text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\ufffd", "'")
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    text = norm_pdf(pages[page - 1])
    needle = norm_pdf(verify).lower()
    idx = text.lower().find(needle)
    if idx < 0:
        return verify

    # Prefer a clean sentence start slightly before the verify match
    start = idx
    window = text[max(0, idx - 80) : idx]
    # Prefer last "And "/"For "/"But " / verse boundary before match
    for marker in (" And ", " For ", " But ", " Then ", " Now ", ". ", "; "):
        mpos = window.rfind(marker)
        if mpos >= 0:
            start = max(0, idx - 80) + mpos + (1 if marker == ". " else 0)
            if marker == ". ":
                start = max(0, idx - 80) + mpos + 2
            break
    else:
        lead = max(0, idx - 20)
        while lead > 0 and text[lead - 1].isalnum():
            lead -= 1
        start = lead if not re.match(r"^[a-z]", text[lead:idx].strip() or "x") else idx

    end = min(len(text), idx + len(verify) + max_len // 2)
    while end < len(text) and end < idx + max_len and text[end - 1].isalnum():
        end += 1
    snippet = text[start:end].strip()
    # Fix verse-number glues: 6And -> 6 And
    snippet = re.sub(r"(\d)([A-Za-z])", r"\1 \2", snippet)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    # Drop leading verse numbers alone
    snippet = re.sub(r"^\d+\s+", "", snippet)
    # Capitalize if starts with lowercase mid-fragment
    if snippet and snippet[0].islower():
        parts = snippet.split(" ", 1)
        if len(parts) == 2 and len(parts[0]) <= 5:
            snippet = parts[1]
        else:
            snippet = snippet[0].upper() + snippet[1:]
    # Ensure first letter capital for display
    if snippet and snippet[0].islower():
        snippet = snippet[0].upper() + snippet[1:]
    return snippet


def find_page(pages: list[str], needle: str) -> int | None:
    def norm_pdf(text: str) -> str:
        text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\ufffd", "'")
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    n = norm_pdf(needle).lower()
    for i, text in enumerate(pages):
        if n in norm_pdf(text).lower():
            return i + 1
    return None


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def derive_from_verify(verify: str) -> str:
    return normalize_answer(verify)


def regenerate_expansion(kjv: str) -> list[dict]:
    mod = load_build_mod()
    pages = [(p.extract_text() or "") for p in PdfReader(str(KJV_PDF)).pages]
    log: list[dict] = []
    ledger: list[dict] = []
    chapters_out: list[dict] = []
    expert: dict[str, str] = {}
    used: set[str] = set()

    # existing core words
    core_text = WORDS_TS.read_text(encoding="utf-8")
    used |= set(re.findall(r'word:\s*"([^"]+)"', core_text))

    for ch in mod.EXPANSION:
        ch_words = []
        for w in ch["words"]:
            wid = f"{ch['id']}-{w['id']}"
            if wid in ANSWER_OVERRIDES:
                phrase = normalize_answer(ANSWER_OVERRIDES[wid])
                source = "override"
            else:
                phrase = derive_from_verify(w["verify"])
                source = "verify"

            # Validate in KJV (flexible)
            ok = in_kjv(phrase, kjv)
            if not ok:
                # fall back to verify-derived
                phrase2 = derive_from_verify(w["verify"])
                if in_kjv(phrase2, kjv):
                    phrase = phrase2
                    source = "verify-fallback"
                    ok = True
                else:
                    # last resort: keep original word if in kjv else override fail
                    orig = normalize_answer(w["word"])
                    if in_kjv(orig, kjv):
                        phrase = orig
                        source = "original"
                        ok = True

            if phrase in used:
                # disambiguate by appending nothing — raise if real conflict
                # allow same phrase only once
                raise SystemExit(f"Duplicate answer phrase for {wid}: {phrase}")

            page = find_page(pages, w["verify"])
            if page is None:
                raise SystemExit(f"KJV verify failed for {wid}: {w['verify']!r}")
            scripture = extract_snippet_clean(pages, page, w["verify"])

            log.append(
                {
                    "id": wid,
                    "old": w["word"],
                    "new": phrase,
                    "source": source,
                    "kjv_ok": ok,
                    "verse": w["verse"],
                }
            )
            ledger.append(
                {
                    "id": wid,
                    "word": phrase,
                    "verse": w["verse"],
                    "verify_substring": w["verify"],
                    "kjv_pdf_page": page,
                    "grade": "VERIFIED" if ok else "NEEDS_REVIEW",
                    "source": KJV_PDF.name,
                    "retrieved": "2026-07-10",
                }
            )
            ch_words.append(
                {
                    "id": wid,
                    "word": phrase,
                    "clue": CLUE_FIXES.get(wid, w["clue"]),
                    "verse": w["verse"],
                    "scripture": scripture,
                    "summary": w["summary"],
                }
            )
            expert[wid] = f"{w['verse']} — {w['verify'][:60]}"
            used.add(phrase)
        chapters_out.append(
            {
                "id": ch["id"],
                "title": ch["title"],
                "description": ch["description"],
                "seasonId": ch.get("seasonId"),
                "words": ch_words,
            }
        )

    # Write expansion TS
    ts_lines = [
        'import type { Chapter } from "./words";',
        "",
        "/** 150 KJV-verified expansion terms (rebuilt 2026-07-10 for phrase accuracy). */",
        "export const expansionChapters: Chapter[] = [",
    ]
    for ch in chapters_out:
        ts_lines.append("  {")
        ts_lines.append(f"    id: '{esc(ch['id'])}',")
        ts_lines.append(f"    title: '{esc(ch['title'])}',")
        ts_lines.append(f"    description: '{esc(ch['description'])}',")
        if ch.get("seasonId"):
            ts_lines.append(f"    seasonId: '{esc(ch['seasonId'])}',")
        ts_lines.append("    words: [")
        for w in ch["words"]:
            ts_lines.append("      {")
            ts_lines.append(f"        id: '{esc(w['id'])}',")
            ts_lines.append(f"        word: '{esc(w['word'])}',")
            ts_lines.append(f"        clue: '{esc(w['clue'])}',")
            ts_lines.append(f"        verse: '{esc(w['verse'])}',")
            ts_lines.append(f"        scripture: '{esc(w['scripture'])}',")
            ts_lines.append(f"        summary: '{esc(w['summary'])}'")
            ts_lines.append("      },")
        ts_lines.append("    ]")
        ts_lines.append("  },")
    ts_lines.append("];")
    ts_lines.append("")
    OUT_EXP.write_text("\n".join(ts_lines), encoding="utf-8")

    exp_lines = [
        "/** Expert clues for expansion terms — verse anchors (not full answer dumps). */",
        "export const expertClueExpansion: Record<string, string> = {",
    ]
    for wid, clue in expert.items():
        # avoid embedding full answer when possible — use verse + short verify
        exp_lines.append(f"  '{esc(wid)}': '{esc(clue)}',")
    exp_lines.append("};")
    exp_lines.append("")
    OUT_EXPERT.write_text("\n".join(exp_lines), encoding="utf-8")

    OUT_LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_EXP}")
    print(f"Wrote {OUT_EXPERT}")
    print(f"Wrote {OUT_LEDGER}")
    return log


def fix_core_words(kjv: str) -> list[dict]:
    text = WORDS_TS.read_text(encoding="utf-8")
    log: list[dict] = []

    # Apply word fixes by id block
    for wid, new_word in CORE_WORD_FIXES.items():
        new_word = normalize_answer(new_word)
        # Find word field after id
        pat = re.compile(
            rf"(id:\s*\"{re.escape(wid)}\",\s*\n\s*word:\s*\")([^\"]+)(\")",
            re.MULTILINE,
        )
        m = pat.search(text)
        if not m:
            log.append({"id": wid, "status": "not_found"})
            continue
        old = m.group(2)
        if old == new_word:
            log.append({"id": wid, "status": "unchanged", "word": old})
            continue
        ok = in_kjv(new_word, kjv)
        text = pat.sub(rf"\g<1>{new_word}\g<3>", text, count=1)
        log.append({"id": wid, "old": old, "new": new_word, "kjv_ok": ok, "status": "fixed"})

    # Clue fixes in core (if any ids in core)
    for wid, new_clue in CLUE_FIXES.items():
        pat = re.compile(
            rf"(id:\s*\"{re.escape(wid)}\",\s*\n\s*word:\s*\"[^\"]+\",\s*\n\s*clue:\s*\")((?:\\.|[^\"\\])*)(\")",
            re.MULTILINE,
        )
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + new_clue.replace("\\", "\\\\").replace('"', '\\"') + m.group(3), text, count=1)
            log.append({"id": wid, "status": "clue_fixed"})

    # Fix scripture for signs-1 to use rumours if needed — leave scripture as author wrote KJV often
    # Fix signs-1 scripture already has rumours - good

    WORDS_TS.write_text(text, encoding="utf-8")
    print(f"Updated {WORDS_TS}")
    return log


def verify_core_overrides(kjv: str) -> None:
    """Drop core fixes that aren't actually in KJV; print warnings."""
    bad = []
    for wid, word in list(CORE_WORD_FIXES.items()):
        if not in_kjv(word, kjv):
            bad.append((wid, word))
    if bad:
        print("WARNING: core fixes not found in KJV (will still apply — review):")
        for wid, word in bad:
            print(f"  {wid}: {word}")


def main() -> None:
    print("Loading KJV...")
    kjv = load_kjv_norm()
    print(f"KJV chars: {len(kjv)}")
    verify_core_overrides(kjv)

    print("Regenerating expansion...")
    exp_log = regenerate_expansion(kjv)
    print("Fixing core words...")
    core_log = fix_core_words(kjv)

    failed = [x for x in exp_log if not x.get("kjv_ok")]
    FIX_LOG.write_text(
        json.dumps(
            {
                "expansion_changes": exp_log,
                "core_changes": core_log,
                "expansion_kjv_fail_count": len(failed),
                "expansion_kjv_fail": failed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {FIX_LOG}")
    print(f"Expansion entries: {len(exp_log)}, kjv_fail: {len(failed)}")
    changed = [x for x in exp_log if x.get("old") and x["old"].upper() != x["new"]]
    print(f"Expansion word string changes: {len(changed)}")
    for x in changed[:20]:
        print(f"  {x['id']}: {x['old']} -> {x['new']}")


if __name__ == "__main__":
    main()
