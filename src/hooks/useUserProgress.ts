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

export function useUserProgress(defaults: UserProgress, todayKey: string) {
  const [progress, setProgress] = useState<UserProgress>(defaults);
  const [syncWarning, setSyncWarning] = useState<string | null>(null);

  const clearSyncWarning = useCallback(() => setSyncWarning(null), []);

  const syncProgressRemote = useCallback(async (p: UserProgress) => {
    if (!supabase || !isSupabaseConfigured) return;
    try {
      const { data } = await supabase.auth.getUser();
      if (!data.user) return;
      const result = await upsertUserProgress(buildUserProgressRow(data.user.id, p));
      if (!result.ok) {
        setSyncWarning(
          "Cloud save failed — progress is still stored on this device. Check your connection and sign-in."
        );
        return;
      }
      setSyncWarning(null);
    } catch (e) {
      console.error("Failed to sync user_progress:", e);
      setSyncWarning(
        "Cloud save failed — progress is still stored on this device. Check your connection and sign-in."
      );
    }
  }, []);

  const saveProgress = useCallback(
    (newProgress: UserProgress) => {
      const { progress: normalized } = unlockCosmeticsForXp(newProgress);
      setProgress(normalized);
      try {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(normalized));
      } catch (e) {
        console.error("Failed to save user progress to localStorage:", e);
        setSyncWarning("Could not save progress on this device (storage full or blocked).");
      }
      void syncProgressRemote(normalized);
    },
    [syncProgressRemote]
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
            setSyncWarning(
              "Cloud save failed — progress is still stored on this device. Check your connection and sign-in."
            );
          }
        },
        onRemoteError: (message) => {
          if (!cancelled) {
            console.error("Remote progress fetch failed:", message);
            setSyncWarning(
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
  }, [todayKey, defaults]);

  return { progress, saveProgress, setProgress, syncWarning, clearSyncWarning };
}
