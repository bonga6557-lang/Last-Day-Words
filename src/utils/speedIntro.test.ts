import { describe, expect, it } from "vitest";
import type { WordTerm } from "../data/words";
import type { UserProgress } from "../types";
import {
  buildIntroWordPool,
  letterCount,
  markSpeedIntroDone,
  needsSpeedIntro,
  SPEED_INTRO_MAX_LETTERS,
} from "./speedIntro";

function term(id: string, word: string): WordTerm {
  return {
    id,
    word,
    clue: "c",
    verse: "v",
    scripture: "s",
    summary: "sum",
  };
}

const base: UserProgress = {
  solvedWordIds: [],
  chapterStars: {},
  speedRoundHighScore: 0,
  speedRoundHighestWordsSolved: 0,
  totalTimePlayedSec: 0,
  soundEnabled: true,
};

describe("speedIntro", () => {
  it("needsSpeedIntro until that board’s intro is marked done", () => {
    expect(needsSpeedIntro(base, "mixed")).toBe(true);
    expect(needsSpeedIntro(base, "chapter")).toBe(true);
    const afterMixed = markSpeedIntroDone(base, "mixed");
    expect(needsSpeedIntro(afterMixed, "mixed")).toBe(false);
    expect(needsSpeedIntro(afterMixed, "chapter")).toBe(true);
    const afterBoth = markSpeedIntroDone(afterMixed, "chapter");
    expect(needsSpeedIntro(afterBoth, "chapter")).toBe(false);
  });

  it("buildIntroWordPool prefers short/easy terms", () => {
    const words = [
      term("a", "SEAL"), // 4 easy
      term("b", "SHAKING"), // 7 easy
      term("c", "WARS AND RUMOURS OF WARS"), // long hard
      term("d", "LATTER RAIN"), // medium-ish
    ];
    const pool = buildIntroWordPool(words);
    expect(pool.every((w) => letterCount(w) <= SPEED_INTRO_MAX_LETTERS || getEasy(w))).toBe(true);
    expect(pool.some((w) => w.id === "c")).toBe(false);
  });

  it("buildIntroWordPool falls back to shortest when few easy words", () => {
    const words = [
      term("long1", "BEHOLD THE BRIDEGROOM COMETH"),
      term("long2", "NATION SHALL RISE AGAINST NATION"),
      term("mid", "PERSECUTION"),
    ];
    const pool = buildIntroWordPool(words);
    expect(pool.length).toBeGreaterThan(0);
    // shortest first when sorted fallback
    expect(letterCount(pool[0])).toBeLessThanOrEqual(letterCount(words[0]));
  });
});

function getEasy(w: WordTerm): boolean {
  return letterCount(w) <= 8;
}
