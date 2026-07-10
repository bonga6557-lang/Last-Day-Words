import { chaptersData } from "../src/data/words";

const fullInClue: { id: string; word: string; clue: string }[] = [];
const partialStrong: { id: string; word: string; clue: string; hit: string }[] = [];

for (const ch of chaptersData) {
  for (const w of ch.words) {
    const word = w.word.toUpperCase();
    const clue = w.clue.toUpperCase();
    if (clue.includes(word)) {
      fullInClue.push({ id: w.id, word: w.word, clue: w.clue });
      continue;
    }
    // multi-word answers: check if clue contains a distinctive 2+ word substring from answer
    const parts = word.split(/\s+/).filter((p) => p.length > 3);
    for (let i = 0; i < parts.length - 1; i++) {
      const phrase = `${parts[i]} ${parts[i + 1]}`;
      if (clue.includes(phrase)) {
        partialStrong.push({ id: w.id, word: w.word, clue: w.clue, hit: phrase });
        break;
      }
    }
  }
}

console.log("REGULAR clues containing FULL answer:", fullInClue.length);
fullInClue.forEach((x) => console.log(`  ${x.id}: ${x.word}`));

console.log("\nREGULAR clues containing 2-word answer phrase:", partialStrong.length);
partialStrong.slice(0, 20).forEach((x) => console.log(`  ${x.id}: "${x.hit}" in ${x.word}`));
