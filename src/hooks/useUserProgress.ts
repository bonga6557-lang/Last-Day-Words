import { useCallback, useEffect, useRef, useState } from "react";
import type { UserProgress } from "../types";
import {
  supabase,
  isSupabaseConfigured,
  fetchUserProgress,
  fetchWeeklyLeaderboardPlacements,
  upsertUserProgress,
  buildUserProgressRow,
} from "../lib/supabase";
import { initializeProgress, LOCAL_STORAGE_KEY } from "../utils/progressInit";
import { getLeaderboardWeekKey, syncLeaderboardPlacements } from "../utils/leaderboard";
import { unlockCosmeticsForXp } from "../utils/progression";
import { logError, mapUserFacingError } from "../utils/errors";

export type ProgressNoticeHandler = (input: {
  tone: "error" | "warning" | "info" | "success";
  message: string;
  sticky?: boolean;
}) => void;

export function useUserProgress(
  defaults: UserProgress,
  todayKey: string,
  onNotice?: ProgressNoticeHandler
) {
  const [progress, setProgress] = useState<UserProgress>(defaults);

  // Keep the notice callback in a ref so `report` stays referentially stable.
  // If `report` changed identity each render, the init effect below would
  // re-run on every render — an infinite init/save loop.
  const onNoticeRef = useRef(onNotice);
  onNoticeRef.current = onNotice;

  const report = useCallback(
    (tone: "error" | "warning" | "info" | "success", message: string, sticky = true) => {
      onNoticeRef.current?.({ tone, message, sticky });
    },
    []
  );

  const syncProgressRemote = useCallback(
    async (p: UserProgress) => {
      if (!supabase || !isSupabaseConfigured) return;
      try {
        const { data } = await supabase.auth.getUser();
        if (!data.user) return;
        const result = await upsertUserProgress(buildUserProgressRow(data.user.id, p));
        if (!result.ok) {
          report(
            "error",
            "Cloud save failed — progress is still stored on this device. Check your connection and sign-in."
          );
          return;
        }
      } catch (e) {
        logError("useUserProgress.sync", e);
        report(
          "error",
          mapUserFacingError(
            e,
            "Cloud save failed — progress is still stored on this device"
          )
        );
      }
    },
    [report]
  );

  // Bumped by every save; an init run whose generation no longer matches is
  // stale and must not apply or write back its (pre-save) result.
  const initGenRef = useRef(0);

  const saveProgress = useCallback(
    (newProgress: UserProgress) => {
      initGenRef.current++;
      const { progress: normalized } = unlockCosmeticsForXp(newProgress);
      setProgress(normalized);
      try {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(normalized));
      } catch (e) {
        logError("useUserProgress.localStorage", e);
        report("error", "Could not save progress on this device (storage full or blocked).");
      }
      void syncProgressRemote(normalized);
    },
    [syncProgressRemote, report]
  );

  useEffect(() => {
    let cancelled = false;
    let lastUserId: string | null | undefined;
    const runInit = async () => {
      const gen = ++initGenRef.current;
      const stale = () => cancelled || initGenRef.current !== gen;
      const loaded = await initializeProgress({
        storageKey: LOCAL_STORAGE_KEY,
        todayKey,
        defaults,
        isRemoteEnabled: Boolean(supabase && isSupabaseConfigured),
        isCancelled: stale,
        getUserId: async () => {
          if (!supabase) return null;
          const { data } = await supabase.auth.getUser();
          lastUserId = data.user?.id ?? null;
          return lastUserId;
        },
        fetchRemote: fetchUserProgress,
        pushRemote: async (userId, p) => {
          const result = await upsertUserProgress(buildUserProgressRow(userId, p));
          if (!result.ok && !cancelled) {
            report(
              "error",
              "Cloud save failed — progress is still stored on this device. Check your connection and sign-in."
            );
          }
        },
        onRemoteError: (message) => {
          if (!cancelled) {
            logError("useUserProgress.fetchRemote", message);
            report(
              "warning",
              "Could not load cloud progress — showing this device's save. Your cloud data was not overwritten."
            );
          }
        },
        reconcileLeaderboard: async (userId, p) => {
          if (!supabase || !isSupabaseConfigured) return p;
          const week = getLeaderboardWeekKey();
          const placements = await fetchWeeklyLeaderboardPlacements(userId, week);
          return syncLeaderboardPlacements(p, week, placements);
        },
      });
      if (!stale()) setProgress(loaded);
    };
    void runInit();

    if (!supabase || !isSupabaseConfigured) {
      return () => {
        cancelled = true;
      };
    }
    const client = supabase;
    const { data: sub } = client.auth.onAuthStateChange((event, s) => {
      // Initial session is covered by the runInit above; token refreshes for
      // the same user must not re-init (a stale re-init can revert fresh saves).
      if (event === "INITIAL_SESSION") return;
      const uid = s?.user?.id ?? null;
      if (uid === lastUserId) return;
      lastUserId = uid;
      // Defer out of the auth callback: awaiting supabase.auth.* inside
      // onAuthStateChange deadlocks on the client's auth lock.
      window.setTimeout(() => {
        if (!cancelled) void runInit();
      }, 0);
    });
    return () => {
      cancelled = true;
      sub.subscription.unsubscribe();
    };
  }, [todayKey, defaults, report]);

  return { progress, saveProgress, setProgress };
}
