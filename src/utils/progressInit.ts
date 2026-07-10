import type { UserProgress } from "../types";
import { unlockCosmeticsForXp, mergeProgression } from "./progression";
import { reconcileStreakOnLoad } from "./streaks";
import { reconcileLeaderboardBadges } from "./leaderboard";
import {
  applyGameState,
  extractGameState,
  mergeGameState,
  parseGameState,
  type GameStateSnapshot,
} from "./progressSync";
import type { UserProgressRow } from "../lib/supabase";
import type { RemoteFetchResult } from "../lib/syncResult";

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
    const withBoard = reconcileLeaderboardBadges(reconciled);
    return unlockCosmeticsForXp(withBoard).progress;
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
  fetchRemote: (userId: string) => Promise<RemoteFetchResult<UserProgressRow>>;
  pushRemote: (userId: string, progress: UserProgress) => Promise<void>;
  storage?: Pick<Storage, "getItem" | "setItem">;
  /**
   * Returns true once this init has been superseded (unmount, newer save, re-init).
   * A stale init must not write back to storage/remote — it would revert
   * anything saved while its remote fetch was in flight.
   */
  isCancelled?: () => boolean;
  /** Called when remote fetch fails so UI can warn without wiping local progress. */
  onRemoteError?: (message: string) => void;
  /** Refresh weekly leaderboard placements from cloud (revokes badges if rank dropped). */
  reconcileLeaderboard?: (userId: string, progress: UserProgress) => Promise<UserProgress>;
}

/** Single init path: localStorage → optional remote merge → one result. */
export async function initializeProgress(opts: InitializeProgressOptions): Promise<UserProgress> {
  const storage = opts.storage ?? localStorage;
  let progress = loadProgressFromStorage(opts.storageKey, opts.todayKey, opts.defaults, storage);

  if (!opts.isRemoteEnabled) return progress;

  const userId = await opts.getUserId();
  if (!userId) return progress;

  const remote = await opts.fetchRemote(userId);
  if (remote.status === "error") {
    // Keep local progress; do NOT push as if this were a new user (would risk overwriting cloud).
    opts.onRemoteError?.(remote.message);
    return progress;
  }

  const cancelled = () => opts.isCancelled?.() ?? false;

  if (remote.status === "empty") {
    progress = unlockCosmeticsForXp(progress).progress;
    if (!cancelled()) await opts.pushRemote(userId, progress);
    return progress;
  }

  progress = mergeWithRemoteRow(progress, remote.data);
  progress = reconcileLeaderboardBadges(progress);
  if (opts.reconcileLeaderboard) {
    progress = await opts.reconcileLeaderboard(userId, progress);
  }
  if (!cancelled()) {
    try {
      storage.setItem(opts.storageKey, JSON.stringify(progress));
    } catch {
      /* ignore quota errors */
    }
    await opts.pushRemote(userId, progress);
  }
  return progress;
}
