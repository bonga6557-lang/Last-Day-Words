/** Max points per solved word: 100 base × 2 combo × 2 golden word. */
export const MAX_SPEED_SCORE_PER_WORD = 400;

/** Upper bound on words_solved claims per round (30s base + time bonuses). */
export const MAX_SPEED_WORDS_PER_ROUND = 80;

export function maxAllowedSpeedScore(wordsSolved: number): number {
  return Math.max(0, wordsSolved) * MAX_SPEED_SCORE_PER_WORD;
}

export function isValidSpeedScore(score: number, wordsSolved: number): boolean {
  return (
    Number.isFinite(score) &&
    Number.isFinite(wordsSolved) &&
    score >= 0 &&
    wordsSolved >= 0 &&
    wordsSolved <= MAX_SPEED_WORDS_PER_ROUND &&
    score <= maxAllowedSpeedScore(wordsSolved)
  );
}
