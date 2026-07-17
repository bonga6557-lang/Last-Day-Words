/**
 * Background video rotation helpers.
 *
 * Three short clips play one after another and loop forever, crossfading at
 * each boundary (see BackgroundVideo). Kept pure/testable here; the component
 * owns the DOM + fade.
 */

/** Ordered background clips in public/. */
export const BACKGROUND_VIDEO_SOURCES: string[] = [
  "/bg-1.mp4",
  "/bg-2.mp4",
  "/bg-3.mp4",
];

/**
 * Index of the next clip to show, wrapping back to the start.
 * Returns 0 for an empty list so callers never index out of range.
 */
export function nextVideoIndex(current: number, length: number): number {
  if (length <= 0) return 0;
  const safe = Number.isFinite(current) ? Math.trunc(current) : 0;
  return ((safe % length) + length + 1) % length;
}
