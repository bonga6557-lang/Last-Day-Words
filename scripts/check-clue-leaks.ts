import { chaptersData } from "../src/data/words";

function tokens(s: string): string[] {
  return s.toUpperCase().replace(/[^A-Z0-9 ]/g, " ").split(/\s+/).filter((t) => t.length > 2);
}

const leaks: { id: string; word: string; clue: string; reason: string }[] = [];

for (const ch of chaptersData) {
  for (const w of ch.words) {
    const wordUp = w.word.toUpperCase();
    const clueUp = w.clue.toUpperCase();
    const expertUp = (w.expertClue ?? "").toUpperCase();

    if (clueUp.includes(wordUp)) {
      leaks.push({ id: w.id, word: w.word, clue: w.clue, reason: "clue contains full answer" });
      continue;
    }

    const wordTokens = tokens(w.word);
    const matched = wordTokens.filter((t) => clueUp.includes(t));
    if (matched.length >= Math.max(2, Math.ceil(wordTokens.length * 0.6))) {
      leaks.push({
        id: w.id,
        word: w.word,
        clue: w.clue,
        reason: `clue shares tokens: ${matched.join(", ")}`,
      });
    }

    if (expertUp.includes(wordUp)) {
      leaks.push({ id: w.id, word: w.word, clue: w.expertClue ?? "", reason: "expert clue contains full answer" });
    }
  }
}

console.log("potential leaks:", leaks.length);
for (const x of leaks.slice(0, 25)) {
  console.log(`- ${x.id} [${x.word}] (${x.reason})`);
  console.log(`  ${x.clue.slice(0, 120)}${x.clue.length > 120 ? "..." : ""}`);
}
