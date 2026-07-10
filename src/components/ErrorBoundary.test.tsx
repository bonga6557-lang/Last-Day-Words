import { describe, expect, it, vi, afterEach } from "vitest";
import { createRoot, type Root } from "react-dom/client";
import { act } from "react";
import ErrorBoundary from "./ErrorBoundary";

function Boom(): null {
  throw new Error("test render boom");
}

describe("ErrorBoundary", () => {
  let container: HTMLDivElement;
  let root: Root;

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  it("renders recovery UI instead of crashing the tree", () => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);

    const spy = vi.spyOn(console, "error").mockImplementation(() => {});

    act(() => {
      root.render(
        <ErrorBoundary name="test">
          <Boom />
        </ErrorBoundary>
      );
    });

    expect(container.textContent).toMatch(/Something went wrong/i);
    expect(container.textContent).toMatch(/test render boom/);
    expect(container.querySelector('[role="alert"]')).toBeTruthy();

    spy.mockRestore();
  });

  it("renders children when there is no error", () => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);

    act(() => {
      root.render(
        <ErrorBoundary>
          <p>All good</p>
        </ErrorBoundary>
      );
    });

    expect(container.textContent).toContain("All good");
  });
});
