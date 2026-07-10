/** Shared local-calendar date helpers — daily and weekly keys use the same timezone policy. */

export function getTodayKey(date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** ISO week key (e.g. 2026-W28) using the local calendar date, matching getTodayKey(). */
export function getIsoWeekKey(date = new Date()): string {
  const local = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const dayNum = local.getDay() || 7;
  local.setDate(local.getDate() + 4 - dayNum);
  const yearStart = new Date(local.getFullYear(), 0, 1);
  const weekNo = Math.ceil(((local.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return `${local.getFullYear()}-W${String(weekNo).padStart(2, "0")}`;
}

const SAST_OFFSET_MS = 2 * 60 * 60 * 1000;

/** SAST calendar parts (UTC+2, no DST). */
function sastParts(date: Date): { y: number; m: number; d: number; dow: number } {
  const t = date.getTime() + SAST_OFFSET_MS;
  const sast = new Date(t);
  return {
    y: sast.getUTCFullYear(),
    m: sast.getUTCMonth() + 1,
    d: sast.getUTCDate(),
    dow: sast.getUTCDay(),
  };
}

/**
 * Weekly speed leaderboard key: Sunday 00:00 SAST through Saturday 23:59 SAST.
 * Returns the Sunday (YYYY-MM-DD) that starts the active board week.
 */
export function getLeaderboardWeekKey(date = new Date()): string {
  const { y, m, d, dow } = sastParts(date);
  const todayUtc = Date.UTC(y, m - 1, d);
  const sundayUtc = todayUtc - dow * 86_400_000;
  const sunday = new Date(sundayUtc);
  const sy = sunday.getUTCFullYear();
  const sm = String(sunday.getUTCMonth() + 1).padStart(2, "0");
  const sd = String(sunday.getUTCDate()).padStart(2, "0");
  return `${sy}-${sm}-${sd}`;
}

export function msUntilLocalMidnight(from = new Date()): number {
  const next = new Date(from.getFullYear(), from.getMonth(), from.getDate() + 1);
  return Math.max(0, next.getTime() - from.getTime());
}
