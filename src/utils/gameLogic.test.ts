import { describe, expect, it } from "vitest";
import { calcStars, getMaxMistakes, getWordDifficulty } from "./gameLogic";
import { chaptersData } from "../data/words";

describe("gameLogic", () => {
  it("calcStars returns 3 for perfect solve without hints", () => {
    expect(calcStars(0, 0)).toBe(3);
    expect(calcStars(1, 0)).toBe(2);
  });

  it("calcStars caps at 2 when hints were used", () => {
    expect(calcStars(0, 1)).toBe(2);
  });

  it("getWordDifficulty tiers by letter count", () => {
    const word = chaptersData[0].words[0];
    expect(["easy", "medium", "hard"]).toContain(getWordDifficulty(word));
    expect(getMaxMistakes("hard")).toBe(4);
    expect(getMaxMistakes("easy")).toBe(5);
  });
});
