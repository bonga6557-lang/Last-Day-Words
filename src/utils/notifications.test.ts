import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import {
  scheduleStreakReminder,
  showStreakAtRiskNotification,
  checkDueStreakReminder,
  getStoredReminderFireAt,
  clearStreakReminderSchedule,
} from "./notifications";

describe("notifications", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    Object.defineProperty(globalThis, "Notification", {
      configurable: true,
      value: class {
        static permission = "granted";
        static requestPermission = vi.fn(async () => "granted");
      },
    });
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: true,
      value: {
        ready: Promise.resolve({
          showNotification: vi.fn(async () => undefined),
        }),
      },
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("does not schedule when daily is already done", () => {
    const clear = scheduleStreakReminder(5, true);
    expect(clear).toBeTypeOf("function");
    vi.advanceTimersByTime(3 * 60 * 60 * 1000);
  });

  it("showStreakAtRiskNotification uses service worker when ready", async () => {
    const registration = await navigator.serviceWorker.ready;
    await showStreakAtRiskNotification(7);
    expect(registration.showNotification).toHaveBeenCalledWith(
      "Last Day Words",
      expect.objectContaining({ tag: "streak-at-risk" })
    );
  });

  it("persists reminder and fires on checkDueStreakReminder after delay", async () => {
    scheduleStreakReminder(5, false);
    expect(getStoredReminderFireAt()).not.toBeNull();
    vi.advanceTimersByTime(2 * 60 * 60 * 1000 + 1);
    checkDueStreakReminder();
    const registration = await navigator.serviceWorker.ready;
    expect(registration.showNotification).toHaveBeenCalled();
    expect(getStoredReminderFireAt()).toBeNull();
  });

  it("clearStreakReminderSchedule removes persisted reminder", () => {
    scheduleStreakReminder(3, false);
    clearStreakReminderSchedule();
    expect(getStoredReminderFireAt()).toBeNull();
  });
});
