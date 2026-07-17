import { describe, expect, it, beforeAll, afterEach } from "vitest";
import { createRoot, type Root } from "react-dom/client";
import { act } from "react";
import BackgroundVideo from "./BackgroundVideo";

// jsdom has no matchMedia (used by useReducedMotion) or media playback.
beforeAll(() => {
  if (!window.matchMedia) {
    window.matchMedia = (query: string) =>
      ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
        addListener: () => {},
        removeListener: () => {},
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList;
  }
  // play() is unimplemented in jsdom — make it a no-op so the component doesn't throw.
  window.HTMLMediaElement.prototype.play = () => Promise.resolve();
  window.HTMLMediaElement.prototype.load = () => {};
});

const SOURCES = ["/a.mp4", "/b.mp4", "/c.mp4"];

describe("BackgroundVideo", () => {
  let container: HTMLDivElement;
  let root: Root;

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  function render() {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    act(() => root.render(<BackgroundVideo sources={SOURCES} fadeMs={0} />));
  }

  const layers = () => ({
    a: container.querySelector<HTMLVideoElement>('[data-testid="bg-video-a"]')!,
    b: container.querySelector<HTMLVideoElement>('[data-testid="bg-video-b"]')!,
  });

  it("starts on the first clip with the second preloaded behind it", () => {
    render();
    const { a, b } = layers();
    expect(a.src).toContain("/a.mp4");
    expect(b.src).toContain("/b.mp4");
    expect(a.style.opacity).toBe("1"); // front
    expect(b.style.opacity).toBe("0"); // back
  });

  it("crossfades to the next clip when the front clip ends and preloads the following one", () => {
    render();
    const { a, b } = layers();

    // Clip A ends -> B becomes front; A (now back) preloads clip C.
    act(() => a.dispatchEvent(new Event("ended")));
    expect(b.style.opacity).toBe("1");
    expect(a.style.opacity).toBe("0");
    expect(a.src).toContain("/c.mp4");

    // Clip B ends -> A becomes front again (showing C); B preloads clip A (wrap).
    act(() => b.dispatchEvent(new Event("ended")));
    expect(a.style.opacity).toBe("1");
    expect(b.style.opacity).toBe("0");
    expect(b.src).toContain("/a.mp4");
  });

  it("ignores 'ended' from the hidden back layer", () => {
    render();
    const { a, b } = layers();
    // B is currently the back layer; its ending must not swap anything.
    act(() => b.dispatchEvent(new Event("ended")));
    expect(a.style.opacity).toBe("1");
    expect(b.style.opacity).toBe("0");
  });
});
