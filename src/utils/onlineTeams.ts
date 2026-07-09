import type { WordTerm } from "../data/words";
import { buildTeamsRound, calcTeamPoints, type TeamId } from "./gameLogic";

export type TeamsPhase = "intro" | "playing" | "turn-result" | "finished";

export type OnlineTeamsPayload = {
  wordIds: string[];
  questionIndex: number;
  phase: TeamsPhase;
  guessedLetters: string[];
  mistakes: number;
  hintsUsed: number;
  letterStreak: number;
  lastTurnPoints: number;
};

export function createOnlineTeamsPayload(allWords: WordTerm[]): OnlineTeamsPayload {
  const round = buildTeamsRound(allWords);
  return {
    wordIds: round.map((w) => w.id),
    questionIndex: 0,
    phase: "intro",
    guessedLetters: [],
    mistakes: 0,
    hintsUsed: 0,
    letterStreak: 0,
    lastTurnPoints: 0,
  };
}

export function activeTeamForIndex(questionIndex: number): TeamId {
  return questionIndex % 2 === 0 ? "white" : "black";
}

export function finishTeamsTurn(
  payload: OnlineTeamsPayload,
  wasSolved: boolean
): { payload: OnlineTeamsPayload; points: number; team: TeamId } {
  const team = activeTeamForIndex(payload.questionIndex);
  const points = calcTeamPoints(
    payload.mistakes,
    payload.hintsUsed,
    wasSolved,
    payload.letterStreak
  );
  return {
    payload: {
      ...payload,
      phase: "turn-result",
      lastTurnPoints: points,
    },
    points,
    team,
  };
}

export function advanceTeamsQuestion(payload: OnlineTeamsPayload): OnlineTeamsPayload {
  if (payload.questionIndex >= payload.wordIds.length - 1) {
    return {
      ...payload,
      phase: "finished",
    };
  }
  return {
    ...payload,
    questionIndex: payload.questionIndex + 1,
    phase: "playing",
    guessedLetters: [],
    mistakes: 0,
    hintsUsed: 0,
    letterStreak: 0,
    lastTurnPoints: 0,
  };
}

export function parseOnlineTeamsPayload(raw: unknown): OnlineTeamsPayload | null {
  if (!raw || typeof raw !== "object") return null;
  const p = raw as Record<string, unknown>;
  if (!Array.isArray(p.wordIds) || p.wordIds.some((id) => typeof id !== "string")) return null;
  if (typeof p.questionIndex !== "number") return null;
  const phase = p.phase;
  if (phase !== "intro" && phase !== "playing" && phase !== "turn-result" && phase !== "finished") {
    return null;
  }
  return {
    wordIds: p.wordIds as string[],
    questionIndex: p.questionIndex,
    phase,
    guessedLetters: Array.isArray(p.guessedLetters) ? (p.guessedLetters as string[]) : [],
    mistakes: typeof p.mistakes === "number" ? p.mistakes : 0,
    hintsUsed: typeof p.hintsUsed === "number" ? p.hintsUsed : 0,
    letterStreak: typeof p.letterStreak === "number" ? p.letterStreak : 0,
    lastTurnPoints: typeof p.lastTurnPoints === "number" ? p.lastTurnPoints : 0,
  };
}
