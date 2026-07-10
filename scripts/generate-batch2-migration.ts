/**
 * Emit supabase migration SQL for batch-2: 20 top-ups + 26 chapters / 130 words.
 */
import { writeFileSync } from "fs";
import { chaptersData } from "../src/data/words";
import { BUNDLED_SEASONS } from "../src/data/seasons";
import { expansionChapters2 } from "../src/data/wordsExpansion2";

function esc(s: string): string {
  return s.replace(/'/g, "''");
}

// Known original 20 chapters that received a 5th top-up word
const TOPUP_CHAPTERS = new Set([
  "signs",
  "shaking",
  "latter-rain",
  "loud-cry",
  "seal-of-god",
  "time-of-trouble",
  "second-coming",
  "new-earth",
  "judgment",
  "deceptions",
  "daniel-image",
  "daniel-beasts",
  "daniel-horn",
  "daniel-sanctuary",
  "daniel-stand",
  "rev-churches",
  "rev-seals",
  "rev-trumpets",
  "rev-beast",
  "rev-millennium",
]);

const topupWords = chaptersData.flatMap((c) =>
  c.words
    .filter((w) => TOPUP_CHAPTERS.has(c.id) && w.id.endsWith("-5"))
    .map((w) => ({ ...w, chapterId: c.id, sort: 4 }))
);

const newChapters = expansionChapters2;
const baseSort = 50;

const lines: string[] = [];
lines.push("-- Batch-2 content: 20 chapter top-ups + 26 new chapters / 130 words (2026-07-10)");
lines.push("-- KJV-verified; see docs/expansion-batch2-ledger.json");
lines.push("");

// chapters
lines.push("insert into public.chapters (id, title, description, sort_order, season_id) values");
lines.push(
  newChapters
    .map((c, i) => {
      const sid = c.seasonId ? `'${esc(c.seasonId)}'` : "null";
      const comma = i === newChapters.length - 1 ? "" : ",";
      return `  ('${esc(c.id)}', '${esc(c.title)}', '${esc(c.description)}', ${baseSort + i}, ${sid})${comma}`;
    })
    .join("\n")
);
lines.push(
  "on conflict (id) do update set title = excluded.title, description = excluded.description, sort_order = excluded.sort_order, season_id = excluded.season_id;"
);
lines.push("");

// season links for new seasonal chapters
const seasonRows: string[] = [];
for (const s of BUNDLED_SEASONS) {
  for (const cid of s.chapterIds) {
    if (newChapters.some((c) => c.id === cid)) {
      seasonRows.push(`  ('${esc(s.id)}', '${esc(cid)}')`);
    }
  }
}
if (seasonRows.length) {
  lines.push("insert into public.season_chapters (season_id, chapter_id) values");
  lines.push(seasonRows.join(",\n"));
  lines.push("on conflict do nothing;");
  lines.push("");
}

// all batch2 words
const wordRows: string[] = [];
for (const w of topupWords) {
  const expert = w.expertClue ? `'${esc(w.expertClue)}'` : "null";
  wordRows.push(
    `  ('${esc(w.id)}', '${esc(w.chapterId)}', '${esc(w.word)}', '${esc(w.clue)}', ${expert}, '${esc(w.verse)}', '${esc(w.scripture)}', '${esc(w.summary)}', ${w.sort})`
  );
}
newChapters.forEach((c) => {
  c.words.forEach((w, wi) => {
    const expert = w.expertClue ? `'${esc(w.expertClue)}'` : "null";
    wordRows.push(
      `  ('${esc(w.id)}', '${esc(c.id)}', '${esc(w.word)}', '${esc(w.clue)}', ${expert}, '${esc(w.verse)}', '${esc(w.scripture)}', '${esc(w.summary)}', ${wi})`
    );
  });
});

lines.push(
  "insert into public.words (id, chapter_id, word, clue, expert_clue, verse, scripture, summary, sort_order) values"
);
lines.push(wordRows.join(",\n"));
lines.push(
  "on conflict (id) do update set chapter_id = excluded.chapter_id, word = excluded.word, clue = excluded.clue, expert_clue = excluded.expert_clue, verse = excluded.verse, scripture = excluded.scripture, summary = excluded.summary, sort_order = excluded.sort_order;"
);
lines.push("");

const out = "supabase/migrations/20260710120000_seed_batch2_content.sql";
writeFileSync(out, lines.join("\n"));
console.log(`Wrote ${out} — topups ${topupWords.length}, new chapters ${newChapters.length}, word rows ${wordRows.length}`);
