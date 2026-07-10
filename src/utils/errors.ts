/**
 * Shared error helpers — normalize unknown throws into safe user-facing copy.
 */

export type ErrorTone = "error" | "warning" | "info" | "success";

export function getErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (error == null) return fallback;
  if (typeof error === "string" && error.trim()) return error.trim();
  if (error instanceof Error && error.message.trim()) return error.message.trim();
  if (typeof error === "object" && error !== null && "message" in error) {
    const m = (error as { message?: unknown }).message;
    if (typeof m === "string" && m.trim()) return m.trim();
  }
  return fallback;
}

export function isNetworkError(error: unknown): boolean {
  const msg = getErrorMessage(error, "").toLowerCase();
  if (typeof navigator !== "undefined" && navigator.onLine === false) return true;
  return (
    msg.includes("failed to fetch") ||
    msg.includes("networkerror") ||
    msg.includes("network request failed") ||
    msg.includes("load failed") ||
    msg.includes("offline") ||
    msg.includes("timeout") ||
    msg.includes("econnrefused") ||
    msg.includes("enotfound")
  );
}

/**
 * Map raw backend / browser errors to short, actionable UI text.
 * Domain-specific mappers (auth) can run first and fall through here.
 */
export function mapUserFacingError(error: unknown, context?: string): string {
  if (typeof navigator !== "undefined" && navigator.onLine === false) {
    return "You appear to be offline. Check your connection and try again.";
  }
  if (isNetworkError(error)) {
    return "Network error. Check your connection and try again.";
  }

  const raw = getErrorMessage(error, "");
  const m = raw.toLowerCase();

  if (m.includes("jwt") || m.includes("not authenticated") || m.includes("session")) {
    return "Your session expired. Sign in again from Account.";
  }
  if (m.includes("permission") || m.includes("row-level security") || m.includes("rls") || m.includes("42501")) {
    return "You don't have permission for that action. Sign in and try again.";
  }
  if (m.includes("duplicate") || m.includes("unique") || m.includes("23505")) {
    return "That name or code is already taken. Try another.";
  }
  if (m.includes("rate") || m.includes("too many")) {
    return "Too many attempts. Wait a moment and try again.";
  }
  if (m.includes("supabase not configured") || m.includes("not configured")) {
    return "Cloud features need Supabase configuration in this environment.";
  }
  if (m.includes("sign in first")) {
    return raw;
  }

  // Prefer short original message when it's already human-readable
  if (raw.length > 0 && raw.length < 160 && !m.includes("postgrest") && !m.includes("pgrst")) {
    return raw;
  }

  return context ? `${context}. Please try again.` : "Something went wrong. Please try again.";
}

export function logError(scope: string, error: unknown, extra?: Record<string, unknown>): void {
  if (extra) {
    console.error(`[${scope}]`, getErrorMessage(error), extra, error);
  } else {
    console.error(`[${scope}]`, getErrorMessage(error), error);
  }
}
