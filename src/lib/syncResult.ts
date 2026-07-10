/** Shared result types for remote progress I/O (distinguish "no row" from "request failed"). */

export type RemoteFetchResult<T> =
  | { status: "ok"; data: T }
  | { status: "empty" }
  | { status: "error"; message: string };

export type RemoteWriteResult = { ok: true } | { ok: false; message: string };

export function writeOk(): RemoteWriteResult {
  return { ok: true };
}

export function writeErr(message: string): RemoteWriteResult {
  return { ok: false, message };
}
