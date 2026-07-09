import { describe, expect, it } from "vitest";
import { getIsoWeekKey, getTodayKey, msUntilLocalMidnight } from "./calendarKeys";

describe("calendarKeys", () => {
  it("getTodayKey uses local calendar components", () => {
    const d = new Date(2026, 6, 9, 23, 59, 0);
    expect(getTodayKey(d)).toBe("2026-07-09");
  });

  it("getIsoWeekKey uses local date for week boundaries", () => {
    const monday = new Date(2026, 6, 6, 12, 0, 0);
    expect(getIsoWeekKey(monday)).toMatch(/^\d{4}-W\d{2}$/);
    expect(getIsoWeekKey(monday)).toBe(getIsoWeekKey(new Date(2026, 6, 6, 23, 0, 0)));
  });

  it("msUntilLocalMidnight is positive before midnight", () => {
    const beforeMidnight = new Date(2026, 6, 9, 12, 0, 0);
    expect(msUntilLocalMidnight(beforeMidnight)).toBeGreaterThan(0);
  });
});
