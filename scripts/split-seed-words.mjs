import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const seedPath = path.join(__dirname, '../supabase/seed_content.sql');
const lines = fs.readFileSync(seedPath, 'utf8').split(/\r?\n/);
const wordsStart = lines.findIndex((l) => l.startsWith('insert into public.words'));
const wordsEnd = lines.findIndex(
  (l, idx) => idx > wordsStart && l.startsWith('on conflict (id) do update'),
);
const wordLines = lines.slice(wordsStart + 1, wordsEnd).filter((l) => l.trim().startsWith("('"));
const header =
  'insert into public.words (id, chapter_id, word, clue, expert_clue, verse, scripture, summary, sort_order) values\n';
const tail =
  'on conflict (id) do update set chapter_id = excluded.chapter_id, word = excluded.word, clue = excluded.clue, expert_clue = excluded.expert_clue, verse = excluded.verse, scripture = excluded.scripture, summary = excluded.summary, sort_order = excluded.sort_order;';

console.log('word rows', wordLines.length);
for (let i = 0; i < 4; i++) {
  const chunk = wordLines.slice(i * 20, (i + 1) * 20);
  const values = chunk
    .map((line, idx) => (idx === chunk.length - 1 ? line.replace(/,\s*$/, '') : line))
    .join('\n');
  const sql = `${header}${values}\n${tail}`;
  const out = path.join(__dirname, `../supabase/_seed_words_${i}.sql`);
  fs.writeFileSync(out, sql);
  console.log('batch', i, chunk.length, 'chars', sql.length);
}
