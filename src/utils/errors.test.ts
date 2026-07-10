import { describe, expect, it } from "vitest";
import { getErrorMessage, isNetworkError, mapUserFacingError } from "./errors";

describe("errors helpers", () => {
  it("getErrorMessage reads Error and strings", () => {
    expect(getErrorMessage(new Error("boom"))).toBe("boom");
    expect(getErrorMessage("plain")).toBe("plain");
    expect(getErrorMessage(null, "fallback")).toBe("fallback");
  });

  it("isNetworkError detects fetch failures", () => {
    expect(isNetworkError(new Error("Failed to fetch"))).toBe(true);
    expect(isNetworkError(new Error("Invalid login"))).toBe(false);
  });

  it("mapUserFacingError keeps short human messages", () => {
    expect(mapUserFacingError(new Error("Sign in first (Account) to create or join a room."))).toMatch(
      /Sign in first/i
    );
  });

  it("mapUserFacingError softens RLS / permission", () => {
    expect(mapUserFacingError(new Error("new row violates row-level security policy"))).toMatch(
      /permission/i
    );
  });
});
