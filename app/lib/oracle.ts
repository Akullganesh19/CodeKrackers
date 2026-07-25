export const predictiveCache: Record<string, Promise<Response | null>> = {};
const MAX_CACHE_SIZE = 10;

/**
 * Pre-computes the scan result for a given text by initiating a background fetch.
 * Results are stored in predictiveCache.
 */
export function preComputeScan(text: string, token: string): void {
  const normalizedText = text.trim();
  if (normalizedText.length < 5) return; // Don't pre-compute for very short texts

  const cacheKey = normalizedText;

  if (cacheKey in predictiveCache) {
    return; // Already pre-computing or cached
  }

  // Eviction policy: keep max 10 entries, delete oldest
  const keys = Object.keys(predictiveCache);
  if (keys.length >= MAX_CACHE_SIZE) {
    delete predictiveCache[keys[0]];
  }

  // Fire background fetch and cache the promise
  const promise = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text: normalizedText })
  }).catch((error) => {
    // Catch and return null to prevent Unhandled Promise Rejections in background
    console.warn('[Oracle] Pre-computation failed:', error);
    return null;
  });

  predictiveCache[cacheKey] = promise;
}

/**
 * Retrieves the scan result. Uses the pre-computed cache if available,
 * otherwise falls back to a native fetch.
 */
export async function getScanResult(text: string, token: string): Promise<Response> {
  const normalizedText = text.trim();
  const cacheKey = normalizedText;

  if (cacheKey in predictiveCache) {
    const cachedPromise = predictiveCache[cacheKey];
    // Delete immediately upon first use to prevent 'body stream already read' error on reuse
    delete predictiveCache[cacheKey];

    const response = await cachedPromise;
    if (response) {
      return response;
    }
  }

  // Fallback to native fetch if cache miss or cached promise resolved to null
  return fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text: normalizedText })
  });
}
