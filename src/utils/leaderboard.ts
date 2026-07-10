import type { BadgeDef, UserProgress } from "../types";
import type { SpeedBoardMode } from "./speedPools";
import { getLeaderboardWeekKey } from "./calendarKeys";
import { STREAK_BADGES } from "./streaks";

export type LeaderboardScoreRow = {
  user_id: string;
  score: number;
  words_solved?: number;
};

export type LeaderboardRanks = {
  weekKey: string;
  mixed?: number | null;
  chapter?: number | null;
};

export type LeaderboardPlacements = {
  mixed: number | null;
  chapter: number | null;
};

export const LEADERBOARD_BADGES: BadgeDef[] = [
  {
    id: "weekly-mixed-1",
    title: "Mixed Speed Champion",
    description: "Currently #1 on the weekly Mixed Speed board (resets Sunday 00:00 SAST).",
    threshold: 1,
  },
  {
    id: "weekly-mixed-2",
    title: "Mixed Speed Silver",
    description: "Currently #2 on the weekly Mixed Speed board (resets Sunday 00:00 SAST).",
    threshold: 2,
  },
  {
    id: "weekly-mixed-3",
    title: "Mixed Speed Bronze",
    description: "Currently #3 on the weekly Mixed Speed board (resets Sunday 00:00 SAST).",
    threshold: 3,
  },
  {
    id: "weekly-chapter-1",
    title: "Chapter Speed Champion",
    description: "Currently #1 on the weekly Chapter Speed board (resets Sunday 00:00 SAST).",
    threshold: 1,
  },
  {
    id: "weekly-chapter-2",
    title: "Chapter Speed Silver",
    description: "Currently #2 on the weekly Chapter Speed board (resets Sunday 00:00 SAST).",
    threshold: 2,
  },
  {
    id: "weekly-chapter-3",
    title: "Chapter Speed Bronze",
    description: "Currently #3 on the weekly Chapter Speed board (resets Sunday 00:00 SAST).",
    threshold: 3,
  },
];

export const LEADERBOARD_BADGE_IDS = new Set(LEADERBOARD_BADGES.map((b) => b.id));
export const STREAK_BADGE_IDS = new Set(STREAK_BADGES.map((b) => b.id));

/** Matches LeaderboardScreen: rows pre-sorted by score desc, rank = index + 1. */
export function assignLeaderboardRanks<T extends LeaderboardScoreRow>(
  rows: readonly T[]
): (T & { rank: number })[] {
  return rows.map((row, i) => ({ ...row, rank: i + 1 }));
}

export function rankForUser(
  userId: string,
  rows: readonly LeaderboardScoreRow[]
): number | null {
  const idx = rows.findIndex((r) => r.user_id === userId);
  return idx === -1 ? null : idx + 1;
}

export function leaderboardBadgeId(mode: SpeedBoardMode, rank: number): string | null {
  if (rank < 1 || rank > 3) return null;
  return `weekly-${mode}-${rank}`;
}

export function leaderboardBadgesFromRanks(ranks: LeaderboardRanks): string[] {
  const ids: string[] = [];
  for (const mode of ["mixed", "chapter"] as const) {
    const rank = ranks[mode];
    if (rank != null && rank >= 1 && rank <= 3) {
      const id = leaderboardBadgeId(mode, rank);
      if (id) ids.push(id);
    }
  }
  return ids;
}

function stripLeaderboardBadgeIds(progress: UserProgress): string[] {
  return (progress.earnedBadgeIds ?? []).filter((id) => !LEADERBOARD_BADGE_IDS.has(id));
}

/** Sync both boards; revokes badges when rank drops below top 3 or week rolls over. */
export function syncLeaderboardPlacements(
  progress: UserProgress,
  weekKey: string,
  placements: LeaderboardPlacements
): UserProgress {
  const nextRanks: LeaderboardRanks = {
    weekKey,
    mixed: placements.mixed,
    chapter: placements.chapter,
  };
  const nonLb = stripLeaderboardBadgeIds(progress);
  const lbBadges = leaderboardBadgesFromRanks(nextRanks);
  return {
    ...progress,
    leaderboardRanks: nextRanks,
    earnedBadgeIds: [...nonLb, ...lbBadges],
  };
}

export function syncLeaderboardPlacementForMode(
  progress: UserProgress,
  weekKey: string,
  mode: SpeedBoardMode,
  rank: number | null
): UserProgress {
  const prev = progress.leaderboardRanks;
  const sameWeek = prev?.weekKey === weekKey;
  return syncLeaderboardPlacements(progress, weekKey, {
    mixed: mode === "mixed" ? rank : sameWeek ? (prev?.mixed ?? null) : null,
    chapter: mode === "chapter" ? rank : sameWeek ? (prev?.chapter ?? null) : null,
  });
}

/** Clear stale weekly badges when the SAST board week changes. */
export function reconcileLeaderboardBadges(
  progress: UserProgress,
  weekKey = getLeaderboardWeekKey()
): UserProgress {
  if (!progress.leaderboardRanks || progress.leaderboardRanks.weekKey !== weekKey) {
    return syncLeaderboardPlacements(progress, weekKey, { mixed: null, chapter: null });
  }
  return syncLeaderboardPlacements(progress, weekKey, {
    mixed: progress.leaderboardRanks.mixed ?? null,
    chapter: progress.leaderboardRanks.chapter ?? null,
  });
}

/** Weekly board keeps the best score for the week, not the latest run. */
export function resolveWeeklySpeedScore(
  existingScore: number | null | undefined,
  roundScore: number
): number {
  return Math.max(existingScore ?? 0, roundScore);
}

export function resolveWeeklyWordsSolved(
  existingScore: number | null | undefined,
  existingWords: number | null | undefined,
  roundScore: number,
  roundWords: number
): number {
  const prevScore = existingScore ?? 0;
  const prevWords = existingWords ?? 0;
  if (roundScore > prevScore) return roundWords;
  if (roundScore === prevScore) return Math.max(prevWords, roundWords);
  return prevWords;
}

export function buildSpeedScoreUpsert(
  existing: { score: number; words_solved: number } | null | undefined,
  round: { score: number; words_solved: number }
): { score: number; words_solved: number } {
  const score = resolveWeeklySpeedScore(existing?.score, round.score);
  const words_solved = resolveWeeklyWordsSolved(
    existing?.score,
    existing?.words_solved,
    round.score,
    round.words_solved
  );
  return { score, words_solved };
}

export { getLeaderboardWeekKey };
