import { describe, expect, it } from "vitest";
import { applySpeedRoundToProgress } from "./speedRoundProgress";
import type { UserProgress } from "../types";

const base: UserProgress = {
  solvedWordIds: [],
  chapterStars: {},
  speedRoundHighScore: 0,
  speedRoundHighestWordsSolved: 0,
  speedMixedHighScore: 400,
  speedMixedHighestWordsSolved: 2,
  totalTimePlayedSec: 0,
  soundEnabled: true,
  xp: 0,
  rank: "novice",
  unlockedCosmetics: ["candle-classic"],
  selectedCandle: "candle-classic",
  selectedBanner: "",
};

describe("applySpeedRoundToProgress", () => {
  it("keeps per-mode highs at the max of prior and round", () => {
    const p = applySpeedRoundToProgress(
      base,
      { finalScore: 300, wordsSolved: 1, perfectCount: 0, mode: "mixed" },
      "2026-07-10"
    );
    expect(p.speedMixedHighScore).toBe(400);
    expect(p.speedMixedHighestWordsSolved).toBe(2);
  });

  it("promotes mixed highs on a better round", () => {
    const p = applySpeedRoundToProgress(
      base,
      { finalScore: 900, wordsSolved: 5, perfectCount: 2, mode: "mixed" },
      "2026-07-10"
    );
    expect(p.speedMixedHighScore).toBe(900);
    expect(p.speedMixedHighestWordsSolved).toBe(5);
    expect(p.speedRoundHighScore).toBe(900);
  });

  it("tracks chapter board highs separately from mixed", () => {
    const p = applySpeedRoundToProgress(
      base,
      { finalScore: 650, wordsSolved: 4, perfectCount: 1, mode: "chapter" },
      "2026-07-10"
    );
    expect(p.speedChapterHighScore).toBe(650);
    expect(p.speedMixedHighScore).toBe(400);
  });

  it("applies perfect-word XP then speed XP from round totals", () => {
    const p = applySpeedRoundToProgress(
      base,
      { finalScore: 340, wordsSolved: 3, perfectCount: 2, mode: "mixed" },
      "2026-07-10"
    );
    // 2 perfect × 25 + floor(340/10) speed XP
    expect(p.xp).toBe(84);
  });

  it("does not advance streak when zero words solved", () => {
    const p = applySpeedRoundToProgress(
      { ...base, dailyChallengeStreak: 2 },
      { finalScore: 0, wordsSolved: 0, perfectCount: 0, mode: "mixed" },
      "2026-07-10"
    );
    expect(p.dailyChallengeStreak).toBe(2);
    expect(p.dailyChallengeCompletedDate).toBeUndefined();
  });

  it("counts any speed run with solves toward the daily streak", () => {
    const p = applySpeedRoundToProgress(
      base,
      { finalScore: 200, wordsSolved: 1, perfectCount: 0, mode: "mixed" },
      "2026-07-10"
    );
    expect(p.dailyChallengeStreak).toBe(1);
    expect(p.dailyChallengeCompletedDate).toBe("2026-07-10");
  });
});
