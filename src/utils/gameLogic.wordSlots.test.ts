/**
 * Smoke tests for pure helpers used by WordSlots / keyboard loop.
 * Full interactive game components stay untested here; utils cover the win condition.
 */
import { describe, expect, it } from "vitest";
import { isWordSolved, normalizeWord, isLetter } from "./gameLogic";

describe("game loop helpers (component surface)", () => {
  it("treats multi-word answers as solved when all letters guessed", () => {
    const text = normalizeWord("BEHOLD THE BRIDEGROOM COMETH");
    const letters = Array.from(new Set(text.split("").filter(isLetter)));
    expect(isWordSolved(text, letters)).toBe(true);
    expect(isWordSolved(text, letters.slice(0, -1))).toBe(false);
  });

  it("ignores punctuation-free spaces for letter slots", () => {
    const text = normalizeWord("A B C");
    expect(text).toBe("A B C");
    expect(isWordSolved(text, ["A", "B", "C"])).toBe(true);
  });
});
