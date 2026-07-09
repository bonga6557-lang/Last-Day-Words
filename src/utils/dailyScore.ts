/** Daily challenge score = sum of star ratings (0–3) per word this run. Max 15 for 5 words. */
export function computeDailyScore(runStars: number[]): number {
  return runStars.reduce((sum, stars) => sum + Math.max(0, Math.min(3, stars)), 0);
}

export function isValidDailyScore(score: number, wordCount: number): boolean {
  const max = wordCount * 3;
  return Number.isFinite(score) && score >= 0 && score <= max;
}
