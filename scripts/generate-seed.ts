import { writeFileSync } from "fs";
import { chaptersData } from "../src/data/words";
import { BUNDLED_SEASONS } from "../src/data/seasons";

function esc(s: string): string {
  return s.replace(/'/g, "''");
}

const lines: string[] = [];
lines.push(`-- Seed content for Last Day Words (${chaptersData.reduce((n, c) => n + c.words.length, 0)} terms / ${chaptersData.length} chapters)`);
lines.push("-- Generated from src/data/words.ts + seasons.ts");
lines.push("");

lines.push("insert into public.seasons (id, title, description, starts_on, ends_on) values");
lines.push(
  BUNDLED_SEASONS.map((s, i) => {
    const comma = i === BUNDLED_SEASONS.length - 1 ? "" : ",";
    return `  ('${esc(s.id)}', '${esc(s.title)}', '${esc(s.description)}', null, null)${comma}`;
  }).join("\n")
);
lines.push(
  "on conflict (id) do update set title = excluded.title, description = excluded.description;"
);
lines.push("");

lines.push("insert into public.chapters (id, title, description, sort_order, season_id) values");
lines.push(
  chaptersData
    .map((c, i) => {
      const sid = c.seasonId ? `'${esc(c.seasonId)}'` : "null";
      const comma = i === chaptersData.length - 1 ? "" : ",";
      return `  ('${esc(c.id)}', '${esc(c.title)}', '${esc(c.description)}', ${i}, ${sid})${comma}`;
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
    seasonLinks.push(`  ('${esc(s.id)}', '${esc(cid)}')`);
  }
}
lines.push("insert into public.season_chapters (season_id, chapter_id) values");
lines.push(seasonLinks.join(",\n"));
lines.push("on conflict do nothing;");
lines.push("");

const wordRows: string[] = [];
chaptersData.forEach((c) => {
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

writeFileSync("supabase/seed_content.sql", lines.join("\n"));
console.log(
  `Wrote supabase/seed_content.sql — ${chaptersData.length} chapters, ${wordRows.length} words`
);
