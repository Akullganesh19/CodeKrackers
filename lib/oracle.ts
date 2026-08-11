// Oracle Predictive Engine Cache
// Stores promises of background scans to achieve zero-latency responses when the user clicks 'Analyze'.

type PredictiveCache = Record<string, Promise<any>>;

const predictiveCache: PredictiveCache = {};
const CACHE_MAX_KEYS = 10; // Eviction policy limit

export function preComputeScan(text: string, token: string | null): void {
  const trimmed = text.trim();
  // Don't precompute if text is too short or if already in cache
  if (trimmed.length < 10 || trimmed in predictiveCache) {
    return;
  }

  // Eviction policy: remove oldest keys if we exceed limit
  const keys = Object.keys(predictiveCache);
  if (keys.length >= CACHE_MAX_KEYS) {
    // Arbitrarily delete the first key to stay under limit
    delete predictiveCache[keys[0]];
  }

  // Launch background request and store the promise
  predictiveCache[trimmed] = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token || 'dummy_token'}`
    },
    body: JSON.stringify({ text: trimmed })
  })
    .then(res => {
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      return res.json();
    })
    .catch(err => {
      // Memory guideline: catch and return null rather than re-throwing to avoid fatal Unhandled Promise Rejection
      console.warn("Oracle: pre-fetch failed silently.", err);
      return null;
    });
}

export function getScanResult(text: string): Promise<any> | undefined {
  const trimmed = text.trim();
  if (trimmed in predictiveCache) {
    return predictiveCache[trimmed];
  }
  return undefined;
}
