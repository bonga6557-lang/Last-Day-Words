import { describe, expect, it, beforeEach, vi } from "vitest";
import {
  areGameSoundsEnabled,
  playAnswerSfx,
  setGameSoundsEnabled,
} from "./sounds";

describe("sounds", () => {
  beforeEach(() => {
    setGameSoundsEnabled(true);
  });

  it("tracks enabled flag", () => {
    setGameSoundsEnabled(false);
    expect(areGameSoundsEnabled()).toBe(false);
    setGameSoundsEnabled(true);
    expect(areGameSoundsEnabled()).toBe(true);
  });

  it("playAnswerSfx does not throw when Audio is stubbed", () => {
    const play = vi.fn(() => Promise.resolve());
    vi.stubGlobal(
      "Audio",
      vi.fn(function MockAudio(this: { play: typeof play; pause: () => void; currentTime: number; volume: number; preload: string }) {
        this.play = play;
        this.pause = vi.fn();
        this.currentTime = 0;
        this.volume = 1;
        this.preload = "auto";
      })
    );
    expect(() => playAnswerSfx(true)).not.toThrow();
    expect(() => playAnswerSfx(false)).not.toThrow();
    setGameSoundsEnabled(false);
    expect(() => playAnswerSfx(true)).not.toThrow();
    vi.unstubAllGlobals();
  });
});
