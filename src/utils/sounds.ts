/**
 * Answer feedback SFX (correct / wrong).
 * Files live in public/sounds/ and are gated by the app sound toggle.
 */

const CORRECT_SRC = "/sounds/correct.mp3";
const WRONG_SRC = "/sounds/wrong.mp3";

let soundsEnabled = true;
let correctAudio: HTMLAudioElement | null = null;
let wrongAudio: HTMLAudioElement | null = null;

function getAudio(kind: "correct" | "wrong"): HTMLAudioElement | null {
  if (typeof Audio === "undefined") return null;
  if (kind === "correct") {
    if (!correctAudio) {
      correctAudio = new Audio(CORRECT_SRC);
      correctAudio.preload = "auto";
      correctAudio.volume = 0.85;
    }
    return correctAudio;
  }
  if (!wrongAudio) {
    wrongAudio = new Audio(WRONG_SRC);
    wrongAudio.preload = "auto";
    wrongAudio.volume = 0.75;
  }
  return wrongAudio;
}

/** Keep in sync with UserProgress.soundEnabled from App. */
export function setGameSoundsEnabled(enabled: boolean): void {
  soundsEnabled = enabled;
}

export function areGameSoundsEnabled(): boolean {
  return soundsEnabled;
}

function play(kind: "correct" | "wrong"): void {
  if (!soundsEnabled) return;
  const audio = getAudio(kind);
  if (!audio) return;
  try {
    audio.pause();
    audio.currentTime = 0;
    const p = audio.play();
    if (p && typeof p.catch === "function") {
      p.catch(() => {
        /* autoplay policy or missing file — ignore */
      });
    }
  } catch {
    /* ignore playback errors */
  }
}

export function playCorrectSound(): void {
  play("correct");
}

export function playWrongSound(): void {
  play("wrong");
}

/** Convenience for letter-guess feedback. */
export function playAnswerSfx(correct: boolean): void {
  if (correct) playCorrectSound();
  else playWrongSound();
}
