/**
 * Writes supabase/migrations/20260709150000_seed_expansion_content.sql
 * from bundled expansion chapters only (30 chapters / 150 words).
 */
import { writeFileSync } from "fs";
import { expansionChapters } from "../src/data/wordsExpansion";
import { BUNDLED_SEASONS } from "../src/data/seasons";

function esc(s: string): string {
  return s.replace(/'/g, "''");
}

const expansionIds = new Set(expansionChapters.map((c) => c.id));
const lines: string[] = [];

lines.push("-- Expansion seed: 30 chapters / 150 KJV-verified words (2026-07-09)");
lines.push("");

const baseSort = 20;
lines.push("insert into public.chapters (id, title, description, sort_order, season_id) values");
lines.push(
  expansionChapters
    .map((c, i) => {
      const sid = c.seasonId ? `'${esc(c.seasonId)}'` : "null";
      const comma = i === expansionChapters.length - 1 ? "" : ",";
      return `  ('${esc(c.id)}', '${esc(c.title)}', '${esc(c.description)}', ${baseSort + i}, ${sid})${comma}`;
    })
    .join("\n")
);
lines.push(
  "on conflict (id) do update set title = excluded.title, description = excluded.description, sort_order = excluded.sort_order, season_id = excluded.season_id;"
);
lines.push("");

const seasonLinks: string[] = [];
for (const s of BUNDLED_SEASONS) {
  for (const cid of s.chapterIds) {
    if (expansionIds.has(cid)) {
      seasonLinks.push(`  ('${esc(s.id)}', '${esc(cid)}')`);
    }
  }
}
lines.push("insert into public.season_chapters (season_id, chapter_id) values");
lines.push(seasonLinks.join(",\n"));
lines.push("on conflict do nothing;");
lines.push("");

const wordRows: string[] = [];
expansionChapters.forEach((c) => {
  c.words.forEach((w, wi) => {
    const expert = w.expertClue ? `'${esc(w.expertClue)}'` : "null";
    wordRows.push(
      `  ('${esc(w.id)}', '${esc(c.id)}', '${esc(w.word)}', '${esc(w.clue)}', ${expert}, '${esc(w.verse)}', '${esc(w.scripture)}', '${esc(w.summary)}', ${wi})`
    );
  });
});

const batchSize = 25;
for (let i = 0; i < wordRows.length; i += batchSize) {
  const chunk = wordRows.slice(i, i + batchSize);
  lines.push(
    "insert into public.words (id, chapter_id, word, clue, expert_clue, verse, scripture, summary, sort_order) values"
  );
  lines.push(chunk.join(",\n"));
  lines.push(
    "on conflict (id) do update set chapter_id = excluded.chapter_id, word = excluded.word, clue = excluded.clue, expert_clue = excluded.expert_clue, verse = excluded.verse, scripture = excluded.scripture, summary = excluded.summary, sort_order = excluded.sort_order;"
  );
  lines.push("");
}

const outPath = "supabase/migrations/20260709150000_seed_expansion_content.sql";
writeFileSync(outPath, lines.join("\n"));
console.log(`Wrote ${outPath} — ${expansionChapters.length} chapters, ${wordRows.length} words`);
