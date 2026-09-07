/**
 * 🛸 Oracle: Predictive Intelligence Engine
 *
 * Anticipates user actions and precomputes data for zero-latency experiences.
 */

const promiseCache: Record<string, Promise<unknown>> = {};
const debounceTimers: Record<string, NodeJS.Timeout> = {};

export function preComputeScan(
  url: string,
  options?: { headers?: Record<string, string>; body?: string; keyOverride?: string }
) {
  const key = options?.keyOverride || url;

  // Debounce by static identifier to avoid per-keystroke timers
  const timerKey = url;

  if (timerKey in debounceTimers) {
    clearTimeout(debounceTimers[timerKey]);
  }

  debounceTimers[timerKey] = setTimeout(() => {
    if (key in promiseCache) return;

    const promise = fetch(url, {
      method: options?.body ? 'POST' : 'GET',
      headers: options?.headers,
      body: options?.body,
    })
      .then((res) => {
        // Clone the response so multiple consumers can read it
        return res.clone();
      })
      .catch((err) => {
        // Delete from cache and DO NOT re-throw to avoid unhandled promise rejections
        delete promiseCache[key];
      });

    promiseCache[key] = promise;
  }, 300); // 300ms debounce after user stops typing
}

export function getScanResult(key: string): Promise<unknown> | null {
  if (key in promiseCache) {
    const p = promiseCache[key] as Promise<Response | void>;
    // Clone again for the consumer
    return p.then((res) => {
      if (res && typeof (res as Response).clone === 'function') {
        return (res as Response).clone();
      }
      return res;
    });
  }
  return null;
}
