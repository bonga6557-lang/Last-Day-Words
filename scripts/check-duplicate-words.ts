import { chaptersData } from "../src/data/words";

const all = chaptersData.flatMap((c) => c.words);
const byWord = new Map<string, string[]>();
const byId = new Map<string, string>();

for (const w of all) {
  const key = w.word.trim().toUpperCase();
  byWord.set(key, [...(byWord.get(key) ?? []), w.id]);
  if (byId.has(w.id)) {
    console.log("DUPLICATE ID:", w.id);
  } else {
    byId.set(w.id, w.word);
  }
}

const dupWords = [...byWord.entries()].filter(([, ids]) => ids.length > 1);

console.log("total words:", all.length);
console.log("unique word strings:", byWord.size);
console.log("unique ids:", byId.size);
console.log("duplicate word strings:", dupWords.length);

for (const [word, ids] of dupWords) {
  console.log(`  ${word} => ${ids.join(", ")}`);
}
