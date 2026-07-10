/** True for local preview/dev hosts where a stale SW breaks lazy-loaded chunks. */
function isLocalHost(): boolean {
  const host = window.location.hostname;
  return (
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "[::1]" ||
    host.endsWith(".local")
  );
}

async function clearServiceWorkerCaches(): Promise<void> {
  if (!("serviceWorker" in navigator)) return;
  const regs = await navigator.serviceWorker.getRegistrations();
  await Promise.all(regs.map((r) => r.unregister()));
  if ("caches" in window) {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => caches.delete(k)));
  }
}

/**
 * On localhost, unregister any SW + caches so preview/dev never serves stale hashed chunks.
 * On production hosts, register the PWA service worker.
 */
export async function initPwa(): Promise<void> {
  if (!("serviceWorker" in navigator)) return;

  if (isLocalHost()) {
    await clearServiceWorkerCaches();
    return;
  }

  if (import.meta.env.PROD) {
    const { registerSW } = await import("virtual:pwa-register");
    registerSW({ immediate: true });
  }
}
