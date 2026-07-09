import { describe, expect, it } from "vitest";
import {
  appendRunSolvedWord,
  isChapterRunComplete,
  isDailyRunComplete,
} from "./runCompletion";

describe("runCompletion", () => {
  const dailyWords = ["w1", "w2", "w3", "w4", "w5"];

  it("rejects daily completion when words were only solved in a prior session (fail-before bug)", () => {
    const globalSolvedIds = [...dailyWords];
    const runSolvedIds: string[] = [];

    const buggyUsesGlobalHistory = dailyWords.every((id) => globalSolvedIds.includes(id));
    expect(buggyUsesGlobalHistory).toBe(true);

    expect(isDailyRunComplete(dailyWords, runSolvedIds)).toBe(false);
  });

  it("accepts daily completion only when every daily word was solved this run", () => {
    expect(isDailyRunComplete(dailyWords, dailyWords)).toBe(true);
    expect(isDailyRunComplete(dailyWords, ["w1", "w2", "w3", "w4"])).toBe(false);
  });

  it("accepts chapter completion from cumulative global solved ids", () => {
    expect(isChapterRunComplete(["a", "b"], ["a", "b", "c"])).toBe(true);
    expect(isChapterRunComplete(["a", "b"], ["a"])).toBe(false);
  });

  it("appendRunSolvedWord adds only successful unique solves", () => {
    expect(appendRunSolvedWord([], "w1", true)).toEqual(["w1"]);
    expect(appendRunSolvedWord(["w1"], "w1", true)).toEqual(["w1"]);
    expect(appendRunSolvedWord(["w1"], "w2", false)).toEqual(["w1"]);
  });
});
