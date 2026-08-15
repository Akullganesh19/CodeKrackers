// Oracle: Predictive Intelligence & Promise Caching
// Enables zero-latency user experiences by fetching data *before* the user explicitly asks for it.

const cache: Record<string, Promise<unknown>> = {};
const EVICTION_LIMIT = 50;

/**
 * Pre-computes a fetch request and caches the in-flight Promise.
 * Call this during user interactions (e.g., typing in a text field)
 * so that when the user submits, the data is already resolved or in-flight.
 */
export function preComputeScan(url: string, payload: Record<string, unknown>, headers: Record<string, string> = {}): void {
  const key = `${url}:${JSON.stringify(payload)}`;

  if (key in cache) {
    return; // Already pre-computing
  }

  // Enforce eviction limit to prevent memory leaks
  const keys = Object.keys(cache);
  if (keys.length >= EVICTION_LIMIT) {
    delete cache[keys[0]]; // Remove oldest
  }

  // Fire the request and cache the promise
  const promise = fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(payload)
  })
    .then(async (res) => {
      if (!res.ok) throw new Error("Pre-compute failed");
      return res.json();
    })
    .catch((err) => {
      console.warn(`[Oracle] Pre-compute failed for ${url}:`, err);
      // Evict failed promises so the actual UI action can retry
      delete cache[key];
      return null;
    });

  cache[key] = promise;
}

/**
 * Retrieves the pre-computed result if available, or returns null.
 * The UI should fallback to a native fetch if this returns null.
 */
export async function getScanResult(url: string, payload: Record<string, unknown>): Promise<unknown> {
  const key = `${url}:${JSON.stringify(payload)}`;

  if (key in cache) {
    const result = await cache[key];
    delete cache[key]; // Consume the result
    return result;
  }

  return null;
}
