import { describe, expect, it } from "vitest";
import { mergeGameState, extractGameState, parseGameState } from "./progressSync";
import type { UserProgress } from "../types";

const base: UserProgress = {
  solvedWordIds: ["a"],
  chapterStars: { signs: 2 },
  speedRoundHighScore: 100,
  speedRoundHighestWordsSolved: 3,
  totalTimePlayedSec: 0,
  soundEnabled: true,
  dailyChallengeStreak: 2,
  wordStats: { a: { timesSolved: 1, struggles: 0, bestStars: 3, mastered: true } },
  xp: 50,
  rank: "novice",
  unlockedCosmetics: ["candle-classic"],
  selectedCandle: "candle-classic",
  selectedBanner: "",
};

describe("progressSync", () => {
  it("unions solvedWordIds and takes max chapter stars", () => {
    const local = extractGameState(base);
    const remote = extractGameState({
      ...base,
      solvedWordIds: ["b"],
      chapterStars: { signs: 3, shaking: 1 },
      dailyChallengeStreak: 5,
    });
    const merged = mergeGameState(local, remote);
    expect(merged.solvedWordIds.sort()).toEqual(["a", "b"]);
    expect(merged.chapterStars).toEqual({ signs: 3, shaking: 1 });
    expect(merged.dailyChallengeStreak).toBe(5);
  });

  it("parseGameState rejects invalid payloads", () => {
    expect(parseGameState(null)).toBeNull();
    expect(parseGameState({})).toBeNull();
    expect(parseGameState({ solvedWordIds: ["x"] })).not.toBeNull();
  });
});
