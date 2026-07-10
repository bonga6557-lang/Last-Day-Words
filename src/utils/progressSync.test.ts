import { describe, expect, it } from "vitest";
import { mergeGameState, extractGameState, parseGameState } from "./progressSync";
import type { UserProgress } from "../types";

const base: UserProgress = {
  solvedWordIds: ["a"],
  chapterStars: { signs: 2 },
  speedRoundHighScore: 100,
  speedRoundHighestWordsSolved: 3,
  speedMixedHighScore: 400,
  speedMixedHighestWordsSolved: 2,
  speedChapterHighScore: 250,
  speedChapterHighestWordsSolved: 1,
  totalTimePlayedSec: 0,
  soundEnabled: true,
  dailyChallengeStreak: 2,
  earnedBadgeIds: ["week-warrior", "weekly-mixed-1"],
  leaderboardRanks: { weekKey: "2026-07-12", mixed: 1, chapter: null },
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
    const merged = mergeGameState(local, remote, "2026-07-12");
    expect(merged.solvedWordIds.sort()).toEqual(["a", "b"]);
    expect(merged.chapterStars).toEqual({ signs: 3, shaking: 1 });
    expect(merged.dailyChallengeStreak).toBe(5);
  });

  it("merges per-mode speed highs across devices", () => {
    const local = extractGameState(base);
    const remote = extractGameState({
      ...base,
      speedMixedHighScore: 900,
      speedMixedHighestWordsSolved: 6,
      speedChapterHighScore: 100,
    });
    const merged = mergeGameState(local, remote, "2026-07-12");
    expect(merged.speedMixedHighScore).toBe(900);
    expect(merged.speedMixedHighestWordsSolved).toBe(6);
    expect(merged.speedChapterHighScore).toBe(250);
  });

  it("recomputes leaderboard badges from merged ranks (no sticky union)", () => {
    const local = extractGameState({
      ...base,
      earnedBadgeIds: ["week-warrior", "weekly-mixed-1"],
      leaderboardRanks: { weekKey: "2026-07-12", mixed: 1, chapter: null },
    });
    const remote = extractGameState({
      ...base,
      earnedBadgeIds: ["week-warrior", "weekly-chapter-2"],
      leaderboardRanks: { weekKey: "2026-07-12", mixed: 3, chapter: 2 },
    });
    const merged = mergeGameState(local, remote, "2026-07-12");
    expect(merged.earnedBadgeIds).toEqual([
      "week-warrior",
      "weekly-mixed-1",
      "weekly-chapter-2",
    ]);
    expect(merged.leaderboardRanks).toEqual({
      weekKey: "2026-07-12",
      mixed: 1,
      chapter: 2,
    });
  });

  it("drops stale leaderboard badges when week key does not match", () => {
    const local = extractGameState({
      ...base,
      earnedBadgeIds: ["weekly-mixed-1"],
      leaderboardRanks: { weekKey: "2026-07-05", mixed: 1, chapter: null },
    });
    const remote = extractGameState({
      ...base,
      earnedBadgeIds: ["week-warrior"],
      leaderboardRanks: undefined,
    });
    const merged = mergeGameState(local, remote, "2026-07-12");
    expect(merged.earnedBadgeIds).not.toContain("weekly-mixed-1");
    expect(merged.leaderboardRanks?.weekKey).toBe("2026-07-12");
  });

  it("parseGameState rejects invalid payloads", () => {
    expect(parseGameState(null)).toBeNull();
    expect(parseGameState({})).toBeNull();
    expect(parseGameState({ solvedWordIds: ["x"] })).not.toBeNull();
  });
});
