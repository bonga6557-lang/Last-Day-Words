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

  const syncProgressRemote = useCallback(async (p: UserProgress) => {
    if (!supabase || !isSupabaseConfigured) return;
    try {
      const { data } = await supabase.auth.getUser();
      if (!data.user) return;
      await upsertUserProgress(buildUserProgressRow(data.user.id, p));
    } catch (e) {
      console.error("Failed to sync user_progress:", e);
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
          await upsertUserProgress(buildUserProgressRow(userId, p));
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

  return { progress, saveProgress, setProgress };
}
