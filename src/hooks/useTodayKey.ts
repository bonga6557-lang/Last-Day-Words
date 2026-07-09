import { useEffect, useState } from "react";
import { getTodayKey, msUntilLocalMidnight } from "../utils/calendarKeys";

/** Local calendar day key that rolls over at local midnight. */
export function useTodayKey(): string {
  const [todayKey, setTodayKey] = useState(() => getTodayKey());

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const schedule = () => {
      timer = setTimeout(() => {
        setTodayKey(getTodayKey());
        schedule();
      }, msUntilLocalMidnight() + 50);
    };
    schedule();
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, []);

  return todayKey;
}
