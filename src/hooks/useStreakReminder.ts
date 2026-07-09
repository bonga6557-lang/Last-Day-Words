import { useEffect } from "react";
import type { UserProgress } from "../types";
import { checkDueStreakReminder, scheduleStreakReminder } from "../utils/notifications";

export function useStreakReminder(progress: UserProgress, todayKey: string): void {
  useEffect(() => {
    checkDueStreakReminder();
    const onVisible = () => checkDueStreakReminder();
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, []);

  useEffect(() => {
    const streak = progress.dailyChallengeStreak ?? 0;
    const dailyDone = progress.dailyChallengeCompletedDate === todayKey;
    if (progress.notificationsEnabled && streak > 0 && !dailyDone) {
      return scheduleStreakReminder(streak, dailyDone);
    }
  }, [
    progress.notificationsEnabled,
    progress.dailyChallengeStreak,
    progress.dailyChallengeCompletedDate,
    todayKey,
  ]);
}
