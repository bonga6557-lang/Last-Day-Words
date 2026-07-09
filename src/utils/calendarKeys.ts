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

export function msUntilLocalMidnight(from = new Date()): number {
  const next = new Date(from.getFullYear(), from.getMonth(), from.getDate() + 1);
  return Math.max(0, next.getTime() - from.getTime());
}
