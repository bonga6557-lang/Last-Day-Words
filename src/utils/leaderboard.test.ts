import { describe, expect, it } from "vitest";
import {
  LEADERBOARD_BADGES,
  assignLeaderboardRanks,
  buildSpeedScoreUpsert,
  leaderboardBadgeId,
  rankForUser,
  reconcileLeaderboardBadges,
  resolveWeeklySpeedScore,
  resolveWeeklyWordsSolved,
  syncLeaderboardPlacementForMode,
  syncLeaderboardPlacements,
} from "./leaderboard";
import type { UserProgress } from "../types";

const base: UserProgress = {
  solvedWordIds: [],
  chapterStars: {},
  speedRoundHighScore: 0,
  speedRoundHighestWordsSolved: 0,
  totalTimePlayedSec: 0,
  soundEnabled: true,
};

describe("leaderboard ranking", () => {
  const board = [
    { user_id: "a", score: 900 },
    { user_id: "b", score: 700 },
    { user_id: "c", score: 500 },
    { user_id: "d", score: 200 },
  ];

  it("assigns ranks by sorted order (score desc)", () => {
    const ranked = assignLeaderboardRanks(board);
    expect(ranked.map((r) => r.rank)).toEqual([1, 2, 3, 4]);
    expect(ranked[0].user_id).toBe("a");
  });

  it("rankForUser returns placement or null", () => {
    expect(rankForUser("b", board)).toBe(2);
    expect(rankForUser("missing", board)).toBeNull();
  });
});

describe("weekly speed score upsert accuracy", () => {
  it("keeps the higher weekly score when a worse run finishes", () => {
    expect(resolveWeeklySpeedScore(1200, 800)).toBe(1200);
    expect(
      buildSpeedScoreUpsert({ score: 1200, words_solved: 6 }, { score: 800, words_solved: 5 })
    ).toEqual({ score: 1200, words_solved: 6 });
  });

  it("promotes weekly score and words on a better run", () => {
    expect(
      buildSpeedScoreUpsert({ score: 600, words_solved: 4 }, { score: 900, words_solved: 7 })
    ).toEqual({ score: 900, words_solved: 7 });
  });

  it("keeps max words when score ties", () => {
    expect(resolveWeeklyWordsSolved(900, 5, 900, 7)).toBe(7);
    expect(resolveWeeklyWordsSolved(900, 8, 900, 7)).toBe(8);
  });

  it("seeds first weekly entry from the round", () => {
    expect(buildSpeedScoreUpsert(null, { score: 340, words_solved: 3 })).toEqual({
      score: 340,
      words_solved: 3,
    });
  });
});

describe("leaderboard badges", () => {
  const week = "2026-07-12";

  it("defines six weekly badges (top 3 × mixed/chapter)", () => {
    expect(LEADERBOARD_BADGES).toHaveLength(6);
    expect(leaderboardBadgeId("mixed", 1)).toBe("weekly-mixed-1");
    expect(leaderboardBadgeId("chapter", 3)).toBe("weekly-chapter-3");
    expect(leaderboardBadgeId("mixed", 4)).toBeNull();
  });

  it("awards the matching badge for top-three placement", () => {
    const p = syncLeaderboardPlacementForMode(base, week, "mixed", 2);
    expect(p.earnedBadgeIds).toEqual(["weekly-mixed-2"]);
    expect(p.leaderboardRanks).toEqual({ weekKey: week, mixed: 2, chapter: null });
  });

  it("revokes badge when rank drops below top three", () => {
    const seeded = syncLeaderboardPlacementForMode(base, week, "mixed", 1);
    const dropped = syncLeaderboardPlacementForMode(seeded, week, "mixed", 4);
    expect(dropped.earnedBadgeIds ?? []).toHaveLength(0);
    expect(dropped.leaderboardRanks?.mixed).toBe(4);
  });

  it("swaps badge when rank changes within top three", () => {
    const first = syncLeaderboardPlacementForMode(base, week, "chapter", 1);
    const second = syncLeaderboardPlacementForMode(first, week, "chapter", 2);
    expect(second.earnedBadgeIds).toEqual(["weekly-chapter-2"]);
    expect(second.earnedBadgeIds).not.toContain("weekly-chapter-1");
  });

  it("mixed and chapter badges are independent", () => {
    let p = syncLeaderboardPlacements(base, week, { mixed: 1, chapter: 3 });
    expect(p.earnedBadgeIds).toEqual(["weekly-mixed-1", "weekly-chapter-3"]);
  });

  it("clears weekly badges when the SAST week rolls over", () => {
    const seeded = syncLeaderboardPlacements(base, "2026-07-05", { mixed: 1, chapter: 2 });
    const rolled = reconcileLeaderboardBadges(seeded, "2026-07-12");
    expect(rolled.earnedBadgeIds ?? []).toHaveLength(0);
    expect(rolled.leaderboardRanks?.weekKey).toBe("2026-07-12");
  });
});
