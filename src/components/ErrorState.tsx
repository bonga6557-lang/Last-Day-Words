import type { ReactNode } from "react";
import { AlertCircle, Inbox, Loader2, RefreshCw, WifiOff } from "lucide-react";

interface InlineAlertProps {
  tone?: "error" | "warning" | "info" | "success";
  title?: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

const toneBox: Record<NonNullable<InlineAlertProps["tone"]>, string> = {
  error: "bg-rose-50 border-rose-200 text-rose-900",
  warning: "bg-[#fbeccb] border-[#e6c98a] text-[#92400e]",
  info: "bg-[#fbf5e9] border-[#e2d2ac] text-[#5c4a33]",
  success: "bg-emerald-50 border-emerald-200 text-emerald-900",
};

/** Compact in-form / in-screen alert. */
export function InlineAlert({
  tone = "error",
  title,
  message,
  actionLabel,
  onAction,
  className = "",
}: InlineAlertProps) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`rounded-xl border px-4 py-3 text-sm text-left space-y-2 ${toneBox[tone]} ${className}`}
    >
      <div className="flex items-start gap-2">
        <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" />
        <div className="min-w-0 space-y-1">
          {title && <p className="font-bold text-xs uppercase tracking-wider">{title}</p>}
          <p className="leading-relaxed">{message}</p>
        </div>
      </div>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg border border-current/25 hover:bg-black/5 cursor-pointer"
        >
          <RefreshCw className="w-3 h-3" aria-hidden="true" />
          {actionLabel}
        </button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: "inbox" | "wifi" | "alert";
  actionLabel?: string;
  onAction?: () => void;
  children?: ReactNode;
}

export function EmptyState({
  title,
  message,
  icon = "inbox",
  actionLabel,
  onAction,
  children,
}: EmptyStateProps) {
  const Icon = icon === "wifi" ? WifiOff : icon === "alert" ? AlertCircle : Inbox;
  return (
    <div className="pcard rounded-2xl p-8 text-center space-y-3">
      <div className="w-12 h-12 mx-auto rounded-full bg-[#f0e3c8] border border-[#e2d2ac] flex items-center justify-center text-[#6b5537]">
        <Icon className="w-5 h-5" aria-hidden="true" />
      </div>
      <h3 className="text-base font-display font-bold text-[#2a2018]">{title}</h3>
      <p className="text-sm text-[#5c4a33] leading-relaxed max-w-sm mx-auto">{message}</p>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="inline-flex items-center gap-1.5 mt-2 py-2 px-4 bg-[#2a2018] text-[#f8f1e3] rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" aria-hidden="true" />
          {actionLabel}
        </button>
      )}
      {children}
    </div>
  );
}

export function LoadingBlock({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-[#6b5537]" role="status">
      <Loader2 className="w-6 h-6 animate-spin" aria-hidden="true" />
      <p className="text-sm">{label}</p>
    </div>
  );
}
