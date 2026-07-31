export const predictiveCache: Record<string, Promise<Response | null>> = {};

export function preComputeScan(text: string) {
  if (!text.trim() || text.length < 10) return;

  const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') || 'dummy_token' : 'dummy_token';
  const cacheKey = `scan:${text}`;

  // Don't re-trigger if already in flight or cached
  if (cacheKey in predictiveCache) return;

  // Clean up old cache entries to prevent memory leaks
  const keys = Object.keys(predictiveCache);
  if (keys.length > 50) {
    delete predictiveCache[keys[0]];
  }

  console.log(`[Oracle] Pre-computing scan for text: ${text.substring(0, 20)}...`);

  const promise = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text })
  }).catch(err => {
    console.error("[Oracle] Pre-compute failed", err);
    return null;
  });

  predictiveCache[cacheKey] = promise;
}

export async function getScanResult(text: string): Promise<Response | null> {
  const cacheKey = `scan:${text}`;
  if (cacheKey in predictiveCache) {
    console.log(`[Oracle] Cache hit for text: ${text.substring(0, 20)}...`);
    const promise = predictiveCache[cacheKey];
    delete predictiveCache[cacheKey]; // Consume it
    const res = await promise;
    if (res) {
      return res.clone();
    }
    return null;
  }
  return null;
}
