import { useCallback, useState } from "react";
import type { ErrorTone } from "../utils/errors";

export type AppNotice = {
  id: string;
  tone: ErrorTone;
  message: string;
  /** 0 = sticky until dismissed */
  autoDismissMs?: number;
};

let noticeSeq = 0;

export function useNoticeQueue() {
  const [notices, setNotices] = useState<AppNotice[]>([]);

  const dismissNotice = useCallback((id: string) => {
    setNotices((list) => list.filter((n) => n.id !== id));
  }, []);

  const pushNotice = useCallback(
    (input: { tone: ErrorTone; message: string; autoDismissMs?: number }) => {
      const id = `n-${Date.now()}-${++noticeSeq}`;
      const autoDismissMs = input.autoDismissMs ?? (input.tone === "error" ? 0 : 7000);
      const notice: AppNotice = {
        id,
        tone: input.tone,
        message: input.message,
        autoDismissMs,
      };
      setNotices((list) => {
        // Dedupe identical sticky messages
        if (list.some((n) => n.message === notice.message && n.tone === notice.tone)) {
          return list;
        }
        return [...list.slice(-4), notice];
      });
      if (autoDismissMs > 0) {
        window.setTimeout(() => {
          setNotices((list) => list.filter((n) => n.id !== id));
        }, autoDismissMs);
      }
      return id;
    },
    []
  );

  const pushError = useCallback(
    (message: string, sticky = true) =>
      pushNotice({ tone: "error", message, autoDismissMs: sticky ? 0 : 8000 }),
    [pushNotice]
  );

  const pushWarning = useCallback(
    (message: string) => pushNotice({ tone: "warning", message, autoDismissMs: 9000 }),
    [pushNotice]
  );

  const pushSuccess = useCallback(
    (message: string) => pushNotice({ tone: "success", message, autoDismissMs: 5000 }),
    [pushNotice]
  );

  const clearNotices = useCallback(() => setNotices([]), []);

  return {
    notices,
    pushNotice,
    pushError,
    pushWarning,
    pushSuccess,
    dismissNotice,
    clearNotices,
  };
}

export type NoticeQueue = ReturnType<typeof useNoticeQueue>;
