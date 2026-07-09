import { describe, expect, it } from "vitest";
import { isValidSpeedScore, maxAllowedSpeedScore, MAX_SPEED_SCORE_PER_WORD } from "./speedScoreLimits";

describe("speedScoreLimits", () => {
  it("allows legitimate scores within per-word ceiling", () => {
    expect(isValidSpeedScore(400, 1)).toBe(true);
    expect(isValidSpeedScore(maxAllowedSpeedScore(5), 5)).toBe(true);
  });

  it("rejects spoofed scores above the per-word ceiling", () => {
    expect(isValidSpeedScore(999999, 1)).toBe(false);
    expect(isValidSpeedScore(MAX_SPEED_SCORE_PER_WORD + 1, 1)).toBe(false);
  });

  it("rejects negative or excessive word counts", () => {
    expect(isValidSpeedScore(100, -1)).toBe(false);
    expect(isValidSpeedScore(100, 81)).toBe(false);
  });
});
