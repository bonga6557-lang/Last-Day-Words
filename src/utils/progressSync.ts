import type { UserProgress, WordStat } from "../types";

/** Fields stored in user_progress.game_state (everything except rank/xp/cosmetics columns). */
export type GameStateSnapshot = Omit<
  UserProgress,
  "xp" | "rank" | "unlockedCosmetics" | "selectedCandle" | "selectedBanner"
>;

export function extractGameState(progress: UserProgress): GameStateSnapshot {
  return {
    solvedWordIds: progress.solvedWordIds,
    chapterStars: progress.chapterStars,
    speedRoundHighScore: progress.speedRoundHighScore,
    speedRoundHighestWordsSolved: progress.speedRoundHighestWordsSolved,
    totalTimePlayedSec: progress.totalTimePlayedSec,
    soundEnabled: progress.soundEnabled,
    dailyChallengeCompletedDate: progress.dailyChallengeCompletedDate,
    dailyChallengeStreak: progress.dailyChallengeStreak,
    lastStreakDate: progress.lastStreakDate,
    streakFreezes: progress.streakFreezes,
    lastFreezeEarnedWeek: progress.lastFreezeEarnedWeek,
    earnedBadgeIds: progress.earnedBadgeIds,
    masteryUnlocks: progress.masteryUnlocks,
    fragmentIds: progress.fragmentIds,
    fragmentsComplete: progress.fragmentsComplete,
    dailyBonusWordDate: progress.dailyBonusWordDate,
    dailyBonusWordId: progress.dailyBonusWordId,
    wordStats: progress.wordStats,
    notificationsEnabled: progress.notificationsEnabled,
    displayName: progress.displayName,
    studyGuideXpDate: progress.studyGuideXpDate,
  };
}

export function applyGameState(progress: UserProgress, snapshot: GameStateSnapshot): UserProgress {
  return { ...progress, ...snapshot };
}

function mergeStringArrays(a: string[] = [], b: string[] = []): string[] {
  return Array.from(new Set([...a, ...b]));
}

function mergeRecordMax(a: Record<string, number> = {}, b: Record<string, number> = {}): Record<string, number> {
  const out = { ...a };
  for (const [key, val] of Object.entries(b)) {
    out[key] = Math.max(out[key] ?? 0, val);
  }
  return out;
}

function mergeWordStat(a: WordStat, b: WordStat): WordStat {
  return {
    timesSolved: Math.max(a.timesSolved, b.timesSolved),
    struggles: Math.max(a.struggles, b.struggles),
    bestStars: Math.max(a.bestStars, b.bestStars),
    mastered: a.mastered || b.mastered,
    seen: a.seen || b.seen,
  };
}

function mergeWordStats(
  a: Record<string, WordStat> = {},
  b: Record<string, WordStat> = {}
): Record<string, WordStat> {
  const out = { ...a };
  for (const [id, stat] of Object.entries(b)) {
    out[id] = out[id] ? mergeWordStat(out[id], stat) : { ...stat };
  }
  return out;
}

function latestDate(a?: string, b?: string): string | undefined {
  if (!a) return b;
  if (!b) return a;
  return a >= b ? a : b;
}

function preferTrue(a?: boolean, b?: boolean): boolean | undefined {
  if (a || b) return true;
  return a ?? b;
}

/** Merge two game-state snapshots from different devices (union / max / latest). */
export function mergeGameState(local: GameStateSnapshot, remote: GameStateSnapshot): GameStateSnapshot {
  const fragmentIds = mergeStringArrays(local.fragmentIds, remote.fragmentIds);
  return {
    solvedWordIds: mergeStringArrays(local.solvedWordIds, remote.solvedWordIds),
    chapterStars: mergeRecordMax(local.chapterStars, remote.chapterStars),
    speedRoundHighScore: Math.max(local.speedRoundHighScore, remote.speedRoundHighScore),
    speedRoundHighestWordsSolved: Math.max(
      local.speedRoundHighestWordsSolved,
      remote.speedRoundHighestWordsSolved
    ),
    totalTimePlayedSec: Math.max(local.totalTimePlayedSec, remote.totalTimePlayedSec),
    soundEnabled: remote.soundEnabled ?? local.soundEnabled,
    dailyChallengeCompletedDate: latestDate(local.dailyChallengeCompletedDate, remote.dailyChallengeCompletedDate),
    dailyChallengeStreak: Math.max(local.dailyChallengeStreak ?? 0, remote.dailyChallengeStreak ?? 0),
    lastStreakDate: latestDate(local.lastStreakDate, remote.lastStreakDate),
    streakFreezes: Math.max(local.streakFreezes ?? 0, remote.streakFreezes ?? 0),
    lastFreezeEarnedWeek: latestDate(local.lastFreezeEarnedWeek, remote.lastFreezeEarnedWeek),
    earnedBadgeIds: mergeStringArrays(local.earnedBadgeIds, remote.earnedBadgeIds),
    masteryUnlocks: mergeRecordMax(local.masteryUnlocks, remote.masteryUnlocks),
    fragmentIds,
    fragmentsComplete: preferTrue(local.fragmentsComplete, remote.fragmentsComplete),
    dailyBonusWordDate: latestDate(local.dailyBonusWordDate, remote.dailyBonusWordDate),
    dailyBonusWordId: remote.dailyBonusWordId ?? local.dailyBonusWordId,
    wordStats: mergeWordStats(local.wordStats, remote.wordStats),
    notificationsEnabled: remote.notificationsEnabled ?? local.notificationsEnabled,
    displayName: remote.displayName ?? local.displayName,
    studyGuideXpDate: latestDate(local.studyGuideXpDate, remote.studyGuideXpDate),
  };
}

export function parseGameState(raw: unknown): GameStateSnapshot | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  if (!Array.isArray(o.solvedWordIds)) return null;
  return o as unknown as GameStateSnapshot;
}
