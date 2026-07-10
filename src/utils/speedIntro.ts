import type { WordTerm } from "../data/words";
import type { UserProgress } from "../types";
import { getWordDifficulty, normalizeWord, shuffleArray } from "./gameLogic";
import type { SpeedBoardMode } from "./speedPools";

/** First Mixed / Chapter run uses more time and shorter terms. */
export const SPEED_INTRO_TIME_SEC = 45;

/** Prefer terms at or under this letter count for intro pools. */
export const SPEED_INTRO_MAX_LETTERS = 10;

export function letterCount(word: WordTerm): number {
  return normalizeWord(word.word).replace(/[^A-Z]/g, "").length;
}

/** True until the player finishes (banks) their first round of that board. */
export function needsSpeedIntro(progress: UserProgress, mode: SpeedBoardMode): boolean {
  if (mode === "mixed") return !progress.speedIntroMixedDone;
  return !progress.speedIntroChapterDone;
}

export function markSpeedIntroDone(progress: UserProgress, mode: SpeedBoardMode): UserProgress {
  if (mode === "mixed") {
    if (progress.speedIntroMixedDone) return progress;
    return { ...progress, speedIntroMixedDone: true };
  }
  if (progress.speedIntroChapterDone) return progress;
  return { ...progress, speedIntroChapterDone: true };
}

/**
 * Shorter, easier terms for first-round comfort.
 * Falls back to shortest words in the board if few "easy" terms exist (e.g. small chapters).
 */
export function buildIntroWordPool(words: WordTerm[]): WordTerm[] {
  if (words.length === 0) return [];
  const easy = words.filter((w) => getWordDifficulty(w) === "easy");
  if (easy.length >= 3) return easy;

  const short = words.filter((w) => letterCount(w) <= SPEED_INTRO_MAX_LETTERS);
  if (short.length >= 2) return short;

  return [...words].sort((a, b) => letterCount(a) - letterCount(b));
}

/** Intro picks: prefer easy, never weight hard higher (unlike normal weighted pick). */
export function pickIntroWord(available: WordTerm[], fallback: WordTerm[]): WordTerm {
  const pool = available.length > 0 ? available : fallback;
  if (pool.length === 0) {
    throw new Error("pickIntroWord: empty pool");
  }
  const easy = pool.filter((w) => getWordDifficulty(w) === "easy");
  const medium = pool.filter((w) => getWordDifficulty(w) === "medium");
  const preferred = easy.length > 0 ? easy : medium.length > 0 ? medium : pool;
  const shuffled = shuffleArray(preferred);
  return shuffled[0];
}
