import { useCallback, useEffect, useRef, useState } from "react";
import { useReducedMotion } from "motion/react";
import { BACKGROUND_VIDEO_SOURCES, nextVideoIndex } from "../utils/videoPlaylist";

interface BackgroundVideoProps {
  /** Ordered clip URLs; defaults to the bundled background set. */
  sources?: string[];
  /** Crossfade length in ms (forced to 0 when the user prefers reduced motion). */
  fadeMs?: number;
}

/**
 * Full-screen background that plays the clips in order and loops forever,
 * crossfading at each boundary. Two stacked <video> layers alternate: the
 * front one plays while the back one preloads the next clip; on `ended` we
 * fade to the back layer and load the following clip behind it.
 */
export default function BackgroundVideo({
  sources = BACKGROUND_VIDEO_SOURCES,
  fadeMs = 1200,
}: BackgroundVideoProps) {
  const reduce = useReducedMotion();
  const aRef = useRef<HTMLVideoElement>(null);
  const bRef = useRef<HTMLVideoElement>(null);
  const frontRef = useRef<0 | 1>(0);
  const [front, setFront] = useState<0 | 1>(0);
  // Source index loaded in each layer.
  const idxRef = useRef({ 0: 0, 1: nextVideoIndex(0, sources.length) });

  const safePlay = (v: HTMLVideoElement | null) => {
    if (!v) return;
    try {
      const p = v.play?.();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch {
      /* autoplay policy — ignore */
    }
  };

  // Load the initial two clips and start the front layer.
  useEffect(() => {
    if (sources.length === 0) return;
    const a = aRef.current;
    const b = bRef.current;
    idxRef.current = { 0: 0, 1: nextVideoIndex(0, sources.length) };
    if (a) {
      a.src = sources[0];
      a.load();
      safePlay(a);
    }
    if (b) {
      b.src = sources[idxRef.current[1]] ?? sources[0];
      b.load();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sources.join("|")]);

  const handleEnded = useCallback(
    (endedLayer: 0 | 1) => {
      // React only to the layer currently in front.
      if (frontRef.current !== endedLayer) return;
      if (sources.length === 0) return;

      const incomingRef = endedLayer === 0 ? bRef : aRef;
      const outgoingRef = endedLayer === 0 ? aRef : bRef;
      const incoming = incomingRef.current;
      const outgoing = outgoingRef.current;

      // Reveal + play the preloaded back layer.
      if (incoming) {
        try {
          incoming.currentTime = 0;
        } catch {
          /* ignore */
        }
        safePlay(incoming);
      }
      const newFront: 0 | 1 = endedLayer === 0 ? 1 : 0;
      frontRef.current = newFront;
      setFront(newFront);

      // Behind the new front, preload the clip that follows it.
      const shownIdx = idxRef.current[newFront];
      const following = nextVideoIndex(shownIdx, sources.length);
      idxRef.current[endedLayer] = following;
      if (outgoing) {
        outgoing.src = sources[following] ?? sources[0];
        outgoing.load();
      }
    },
    [sources]
  );

  const transition = reduce ? "none" : `opacity ${fadeMs}ms ease`;

  return (
    <>
      <video
        ref={aRef}
        onEnded={() => handleEnded(0)}
        className="bg-video"
        style={{ opacity: front === 0 ? 1 : 0, transition }}
        muted
        playsInline
        preload="auto"
        disablePictureInPicture
        aria-hidden="true"
        data-testid="bg-video-a"
      />
      <video
        ref={bRef}
        onEnded={() => handleEnded(1)}
        className="bg-video"
        style={{ opacity: front === 1 ? 1 : 0, transition }}
        muted
        playsInline
        preload="auto"
        disablePictureInPicture
        aria-hidden="true"
        data-testid="bg-video-b"
      />
    </>
  );
}
