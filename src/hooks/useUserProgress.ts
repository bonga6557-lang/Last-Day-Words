import { useCallback, useEffect, useState } from "react";
import type { UserProgress } from "../types";
import {
  supabase,
  isSupabaseConfigured,
  fetchUserProgress,
  upsertUserProgress,
  buildUserProgressRow,
} from "../lib/supabase";
import { initializeProgress, LOCAL_STORAGE_KEY } from "../utils/progressInit";
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

  const report = useCallback(
    (tone: "error" | "warning" | "info" | "success", message: string, sticky = true) => {
      onNotice?.({ tone, message, sticky });
    },
    [onNotice]
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

  const saveProgress = useCallback(
    (newProgress: UserProgress) => {
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
    const runInit = async () => {
      const loaded = await initializeProgress({
        storageKey: LOCAL_STORAGE_KEY,
        todayKey,
        defaults,
        isRemoteEnabled: Boolean(supabase && isSupabaseConfigured),
        getUserId: async () => {
          if (!supabase) return null;
          const { data } = await supabase.auth.getUser();
          return data.user?.id ?? null;
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
      });
      if (!cancelled) setProgress(loaded);
    };
    void runInit();

    if (!supabase || !isSupabaseConfigured) {
      return () => {
        cancelled = true;
      };
    }
    const client = supabase;
    const { data: sub } = client.auth.onAuthStateChange(() => {
      void runInit();
    });
    return () => {
      cancelled = true;
      sub.subscription.unsubscribe();
    };
  }, [todayKey, defaults, report]);

  return { progress, saveProgress, setProgress };
}
