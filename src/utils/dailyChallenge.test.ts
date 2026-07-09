import { describe, expect, it } from "vitest";
import { getDailyWords, getTodayKey } from "./dailyChallenge";
import { allWordsList } from "../data/words";

describe("dailyChallenge", () => {
  it("getDailyWords is deterministic for the same date", () => {
    const a = getDailyWords(allWordsList, "2026-07-09");
    const b = getDailyWords(allWordsList, "2026-07-09");
    expect(a.map((w) => w.id)).toEqual(b.map((w) => w.id));
  });

  it("getDailyWords differs across dates", () => {
    const a = getDailyWords(allWordsList, "2026-07-09");
    const b = getDailyWords(allWordsList, "2026-07-10");
    expect(a.map((w) => w.id)).not.toEqual(b.map((w) => w.id));
  });

  it("getTodayKey returns YYYY-MM-DD", () => {
    expect(getTodayKey(new Date("2026-07-09T15:00:00"))).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
