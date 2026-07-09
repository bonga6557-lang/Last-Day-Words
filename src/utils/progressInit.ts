import type { UserProgress } from "../types";
import { unlockCosmeticsForXp, mergeProgression } from "./progression";
import { reconcileStreakOnLoad } from "./streaks";
import {
  applyGameState,
  extractGameState,
  mergeGameState,
  parseGameState,
  type GameStateSnapshot,
} from "./progressSync";
import type { UserProgressRow } from "../lib/supabase";

export const LOCAL_STORAGE_KEY = "last_day_words_progress_v1";

export function loadProgressFromStorage(
  storageKey: string,
  todayKey: string,
  defaults: UserProgress,
  storage: Pick<Storage, "getItem"> = localStorage
): UserProgress {
  try {
    const stored = storage.getItem(storageKey);
    if (!stored) return defaults;
    const parsed = JSON.parse(stored) as UserProgress;
    const reconciled = reconcileStreakOnLoad(parsed, todayKey);
    return unlockCosmeticsForXp(reconciled).progress;
  } catch {
    return defaults;
  }
}

export function mergeWithRemoteRow(local: UserProgress, remote: UserProgressRow): UserProgress {
  const withProgression = mergeProgression(local, remote);
  const remoteState = parseGameState(remote.game_state) ?? ({} as GameStateSnapshot);
  const localState = extractGameState(local);
  const mergedState = mergeGameState(localState, remoteState);
  return unlockCosmeticsForXp(applyGameState(withProgression, mergedState)).progress;
}

export interface InitializeProgressOptions {
  storageKey: string;
  todayKey: string;
  defaults: UserProgress;
  isRemoteEnabled: boolean;
  getUserId: () => Promise<string | null>;
  fetchRemote: (userId: string) => Promise<UserProgressRow | null>;
  pushRemote: (userId: string, progress: UserProgress) => Promise<void>;
  storage?: Pick<Storage, "getItem" | "setItem">;
}

/** Single init path: localStorage → optional remote merge → one result. */
export async function initializeProgress(opts: InitializeProgressOptions): Promise<UserProgress> {
  const storage = opts.storage ?? localStorage;
  let progress = loadProgressFromStorage(opts.storageKey, opts.todayKey, opts.defaults, storage);

  if (!opts.isRemoteEnabled) return progress;

  const userId = await opts.getUserId();
  if (!userId) return progress;

  const remote = await opts.fetchRemote(userId);
  if (!remote) {
    progress = unlockCosmeticsForXp(progress).progress;
    await opts.pushRemote(userId, progress);
    return progress;
  }

  progress = mergeWithRemoteRow(progress, remote);
  try {
    storage.setItem(opts.storageKey, JSON.stringify(progress));
  } catch {
    /* ignore quota errors */
  }
  await opts.pushRemote(userId, progress);
  return progress;
}
