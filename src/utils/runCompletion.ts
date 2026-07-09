/** Whether every word in the run was solved during this session (not prior global history). */
export function isDailyRunComplete(dailyWordIds: string[], runSolvedWordIds: string[]): boolean {
  if (dailyWordIds.length === 0) return false;
  const solved = new Set(runSolvedWordIds);
  return dailyWordIds.every((id) => solved.has(id));
}

/** Chapter completion uses cumulative solved-word history across sessions. */
export function isChapterRunComplete(chapterWordIds: string[], globalSolvedWordIds: string[]): boolean {
  if (chapterWordIds.length === 0) return false;
  const solved = new Set(globalSolvedWordIds);
  return chapterWordIds.every((id) => solved.has(id));
}

/** Append a word id to the current run's solved set when solved this attempt. */
export function appendRunSolvedWord(runSolvedWordIds: string[], wordId: string, wordSolved: boolean): string[] {
  if (!wordSolved || runSolvedWordIds.includes(wordId)) return runSolvedWordIds;
  return [...runSolvedWordIds, wordId];
}
