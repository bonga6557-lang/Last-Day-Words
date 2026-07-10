import { writeFileSync } from "fs";
import { chaptersData } from "../src/data/words";

const payload = chaptersData.map((c) => ({
  id: c.id,
  title: c.title,
  seasonId: c.seasonId ?? null,
  words: c.words.map((w) => ({
    id: w.id,
    word: w.word,
    clue: w.clue,
    expertClue: w.expertClue ?? null,
    verse: w.verse,
    scripture: w.scripture,
    summary: w.summary,
  })),
}));

writeFileSync("docs/words-catalog-export.json", JSON.stringify(payload, null, 2));
console.log(
  `Exported ${payload.length} chapters, ${payload.reduce((n, c) => n + c.words.length, 0)} words`
);
