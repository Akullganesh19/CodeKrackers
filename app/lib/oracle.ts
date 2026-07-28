export const predictiveCache: Record<string, Promise<Response | null>> = {};

const MAX_CACHE_SIZE = 50;

export const preComputeScan = (text: string, token: string) => {
  if (!text || text.trim().length < 5) return;

  const key = text.trim();

  if (key in predictiveCache) return;

  // Eviction policy
  const keys = Object.keys(predictiveCache);
  if (keys.length >= MAX_CACHE_SIZE) {
    delete predictiveCache[keys[0]];
  }

  // Pre-compute the request
  const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text: key })
  }).catch((error) => {
    console.error("Predictive fetch failed (silently caught):", error);
    return null;
  });

  predictiveCache[key] = fetchPromise;
};

export const getScanResult = (text: string): Promise<Response | null> | null => {
  const key = text.trim();
  const cachedPromise = predictiveCache[key];
  if (cachedPromise) {
    // Delete from cache on first read to avoid "body stream already read"
    delete predictiveCache[key];
    return cachedPromise;
  }
  return null;
};
