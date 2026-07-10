import type { UserProgress } from "../types";
import { applyDailyStreakComplete } from "./streaks";
import { awardPerfectWordsXp, awardSpeedXp } from "./progression";
import type { SpeedBoardMode } from "./speedPools";
import { markSpeedIntroDone } from "./speedIntro";

export type SpeedRoundResult = {
  finalScore: number;
  wordsSolved: number;
  perfectCount: number;
  mode: SpeedBoardMode;
  /** First-run easy round for this board. */
  wasIntro?: boolean;
};

/** Local progress updates after a speed round (no cloud leaderboard). */
export function applySpeedRoundToProgress(
  progress: UserProgress,
  result: SpeedRoundResult,
  todayKey: string
): UserProgress {
  const { finalScore, wordsSolved, perfectCount, mode, wasIntro } = result;
  const highKey = mode === "mixed" ? "speedMixedHighScore" : "speedChapterHighScore";
  const wordsKey =
    mode === "mixed" ? "speedMixedHighestWordsSolved" : "speedChapterHighestWordsSolved";

  const prevHigh =
    (progress[highKey] as number | undefined) ??
    (mode === "mixed" ? progress.speedRoundHighScore : 0);
  const prevWords =
    (progress[wordsKey] as number | undefined) ??
    (mode === "mixed" ? progress.speedRoundHighestWordsSolved : 0);

  let next: UserProgress = {
    ...progress,
    [highKey]: Math.max(prevHigh, finalScore),
    [wordsKey]: Math.max(prevWords, wordsSolved),
    speedRoundHighScore: Math.max(progress.speedRoundHighScore, finalScore),
    speedRoundHighestWordsSolved: Math.max(progress.speedRoundHighestWordsSolved, wordsSolved),
  };

  next = awardPerfectWordsXp(next, perfectCount).progress;
  next = awardSpeedXp(next, finalScore).progress;

  if (wordsSolved > 0) {
    next = applyDailyStreakComplete(next, todayKey);
  }
  if (wasIntro) {
    next = markSpeedIntroDone(next, mode);
  }
  return next;
}
