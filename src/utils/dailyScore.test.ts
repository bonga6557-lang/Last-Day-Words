import { describe, expect, it } from "vitest";
import { computeDailyScore, isValidDailyScore } from "./dailyScore";

describe("dailyScore", () => {
  it("sums star ratings for the daily run", () => {
    expect(computeDailyScore([3, 2, 3, 1, 3])).toBe(12);
    expect(computeDailyScore([])).toBe(0);
  });

  it("validates score against word count ceiling", () => {
    expect(isValidDailyScore(15, 5)).toBe(true);
    expect(isValidDailyScore(16, 5)).toBe(false);
  });
});
