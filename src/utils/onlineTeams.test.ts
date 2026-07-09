import { describe, expect, it } from "vitest";
import {
  activeTeamForIndex,
  advanceTeamsQuestion,
  createOnlineTeamsPayload,
  finishTeamsTurn,
  parseOnlineTeamsPayload,
} from "./onlineTeams";
import { chaptersData } from "../data/words";

describe("onlineTeams", () => {
  it("createOnlineTeamsPayload seeds word ids for a full round", () => {
    const allWords = chaptersData.flatMap((c) => c.words);
    const payload = createOnlineTeamsPayload(allWords);
    expect(payload.wordIds.length).toBe(20);
    expect(payload.phase).toBe("intro");
  });

  it("finishTeamsTurn moves to turn-result with points", () => {
    const payload = createOnlineTeamsPayload(chaptersData.flatMap((c) => c.words));
    const playing = { ...payload, phase: "playing" as const, mistakes: 0, hintsUsed: 0 };
    const result = finishTeamsTurn(playing, true);
    expect(result.payload.phase).toBe("turn-result");
    expect(result.team).toBe("white");
    expect(result.points).toBeGreaterThan(0);
  });

  it("advanceTeamsQuestion resets turn state", () => {
    const payload = createOnlineTeamsPayload(chaptersData.flatMap((c) => c.words));
    const after = advanceTeamsQuestion({
      ...payload,
      phase: "turn-result",
      questionIndex: 0,
      guessedLetters: ["A"],
      mistakes: 2,
    });
    expect(after.phase).toBe("playing");
    expect(after.questionIndex).toBe(1);
    expect(after.guessedLetters).toEqual([]);
  });

  it("activeTeamForIndex alternates teams", () => {
    expect(activeTeamForIndex(0)).toBe("white");
    expect(activeTeamForIndex(1)).toBe("black");
  });

  it("parseOnlineTeamsPayload rejects invalid shapes", () => {
    expect(parseOnlineTeamsPayload(null)).toBeNull();
    expect(parseOnlineTeamsPayload({ wordIds: ["a"], questionIndex: 0, phase: "nope" })).toBeNull();
  });
});
