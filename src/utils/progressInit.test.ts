import { describe, expect, it, vi } from "vitest";
import { initializeProgress, LOCAL_STORAGE_KEY, loadProgressFromStorage } from "./progressInit";
import type { UserProgress } from "../types";
import type { UserProgressRow } from "../lib/supabase";

const defaults: UserProgress = {
  solvedWordIds: [],
  chapterStars: {},
  speedRoundHighScore: 0,
  speedRoundHighestWordsSolved: 0,
  totalTimePlayedSec: 0,
  soundEnabled: true,
  xp: 0,
  rank: "novice",
  unlockedCosmetics: ["candle-classic"],
  selectedCandle: "candle-classic",
  selectedBanner: "",
};

describe("progressInit", () => {
  it("loads local storage without remote when disabled", async () => {
    const storage = {
      getItem: vi.fn(() => JSON.stringify({ ...defaults, xp: 25 })),
      setItem: vi.fn(),
    };
    const result = await initializeProgress({
      storageKey: LOCAL_STORAGE_KEY,
      todayKey: "2026-07-09",
      defaults,
      isRemoteEnabled: false,
      getUserId: async () => "user-1",
      fetchRemote: async () => ({ status: "empty" as const }),
      pushRemote: async () => {},
      storage,
    });
    expect(result.xp).toBe(25);
    expect(storage.setItem).not.toHaveBeenCalled();
  });

  it("merges remote game_state and xp in one init pass", async () => {
    const storage = {
      getItem: vi.fn(() => JSON.stringify({ ...defaults, solvedWordIds: ["local-word"], xp: 10 })),
      setItem: vi.fn(),
    };
    const remote: UserProgressRow = {
      user_id: "user-1",
      xp: 100,
      rank: "student",
      unlocked_cosmetics: ["candle-classic"],
      selected_candle: "candle-classic",
      selected_banner: "",
      game_state: {
        solvedWordIds: ["remote-word"],
        chapterStars: {},
        speedRoundHighScore: 500,
        speedRoundHighestWordsSolved: 8,
        totalTimePlayedSec: 0,
        soundEnabled: true,
      },
    };
    const pushRemote = vi.fn(async () => {});
    const result = await initializeProgress({
      storageKey: LOCAL_STORAGE_KEY,
      todayKey: "2026-07-09",
      defaults,
      isRemoteEnabled: true,
      getUserId: async () => "user-1",
      fetchRemote: async () => ({ status: "ok" as const, data: remote }),
      pushRemote,
      storage,
    });
    expect(result.xp).toBe(100);
    expect(result.solvedWordIds.sort()).toEqual(["local-word", "remote-word"]);
    expect(result.speedRoundHighScore).toBe(500);
    expect(storage.setItem).toHaveBeenCalledOnce();
    expect(pushRemote).toHaveBeenCalledOnce();
  });

  it("does not push local as new user when remote fetch fails", async () => {
    const storage = {
      getItem: vi.fn(() => JSON.stringify({ ...defaults, xp: 42, solvedWordIds: ["keep-me"] })),
      setItem: vi.fn(),
    };
    const pushRemote = vi.fn(async () => {});
    const onRemoteError = vi.fn();
    const result = await initializeProgress({
      storageKey: LOCAL_STORAGE_KEY,
      todayKey: "2026-07-09",
      defaults,
      isRemoteEnabled: true,
      getUserId: async () => "user-1",
      fetchRemote: async () => ({ status: "error" as const, message: "network down" }),
      pushRemote,
      onRemoteError,
      storage,
    });
    expect(result.xp).toBe(42);
    expect(result.solvedWordIds).toEqual(["keep-me"]);
    expect(pushRemote).not.toHaveBeenCalled();
    expect(onRemoteError).toHaveBeenCalledWith("network down");
  });

  it("loadProgressFromStorage returns defaults when empty", () => {
    const storage = { getItem: vi.fn(() => null) };
    expect(loadProgressFromStorage("key", "2026-07-09", defaults, storage)).toEqual(defaults);
  });
});
