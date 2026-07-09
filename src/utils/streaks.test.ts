import { describe, expect, it } from "vitest";
import { reconcileStreakOnLoad, applyDailyStreakComplete } from "./streaks";
import type { UserProgress } from "../types";

const base: UserProgress = {
  solvedWordIds: [],
  chapterStars: {},
  speedRoundHighScore: 0,
  speedRoundHighestWordsSolved: 0,
  totalTimePlayedSec: 0,
  soundEnabled: true,
};

describe("streaks", () => {
  it("applyDailyStreakComplete increments streak on consecutive days", () => {
    const p = applyDailyStreakComplete(
      { ...base, dailyChallengeCompletedDate: "2026-07-08", dailyChallengeStreak: 3 },
      "2026-07-09"
    );
    expect(p.dailyChallengeStreak).toBe(4);
    expect(p.dailyChallengeCompletedDate).toBe("2026-07-09");
  });

  it("reconcileStreakOnLoad resets streak after missed day without freeze", () => {
    const p = reconcileStreakOnLoad(
      {
        ...base,
        dailyChallengeStreak: 5,
        lastStreakDate: "2026-07-06",
      },
      "2026-07-09"
    );
    expect(p.dailyChallengeStreak).toBe(0);
  });
});
