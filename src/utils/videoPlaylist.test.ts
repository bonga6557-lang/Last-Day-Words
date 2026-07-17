import { describe, expect, it } from "vitest";
import { BACKGROUND_VIDEO_SOURCES, nextVideoIndex } from "./videoPlaylist";

describe("videoPlaylist", () => {
  it("bundles exactly the three background clips", () => {
    expect(BACKGROUND_VIDEO_SOURCES).toEqual(["/bg-1.mp4", "/bg-2.mp4", "/bg-3.mp4"]);
  });

  it("advances and wraps around the playlist", () => {
    expect(nextVideoIndex(0, 3)).toBe(1);
    expect(nextVideoIndex(1, 3)).toBe(2);
    expect(nextVideoIndex(2, 3)).toBe(0); // wrap
  });

  it("cycles through every clip in order without gaps", () => {
    const order: number[] = [];
    let i = 0;
    for (let step = 0; step < 6; step++) {
      order.push(i);
      i = nextVideoIndex(i, 3);
    }
    expect(order).toEqual([0, 1, 2, 0, 1, 2]);
  });

  it("is robust to empty, negative, and out-of-range inputs", () => {
    expect(nextVideoIndex(0, 0)).toBe(0);
    expect(nextVideoIndex(5, 3)).toBe(0); // 5 % 3 = 2 -> next 0
    expect(nextVideoIndex(-1, 3)).toBe(0); // -1 wraps to 2 -> next 0
    expect(nextVideoIndex(NaN, 3)).toBe(1);
  });
});
