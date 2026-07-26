// Predictive intelligence module

type CacheEntry = {
  promise: Promise<Response | null>;
  timestamp: number;
};

const MAX_CACHE_SIZE = 10;
const predictiveCache: Record<string, CacheEntry> = {};

function evictOldestIfNeeded() {
  const keys = Object.keys(predictiveCache);
  if (keys.length > MAX_CACHE_SIZE) {
    let oldestKey = keys[0];
    let oldestTimestamp = predictiveCache[oldestKey].timestamp;

    for (const key of keys) {
      if (predictiveCache[key].timestamp < oldestTimestamp) {
        oldestTimestamp = predictiveCache[key].timestamp;
        oldestKey = key;
      }
    }

    delete predictiveCache[oldestKey];
  }
}

export const Oracle = {
  preComputeScan: (text: string, token: string) => {
    if (!text.trim()) return;

    const key = text.trim();
    if (predictiveCache[key]) return; // Already computing or computed

    // Start background fetch
    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).catch(err => {
      console.error("Oracle background fetch error:", err);
      return null; // Return null instead of re-throwing for unawaited background promise
    });

    predictiveCache[key] = {
      promise: fetchPromise,
      timestamp: Date.now()
    };

    evictOldestIfNeeded();
  },

  getScanResult: async (text: string, token: string): Promise<Response | null> => {
    const key = text.trim();
    if (!key) return null;

    const cacheEntry = predictiveCache[key];
    if (cacheEntry) {
      delete predictiveCache[key]; // Delete immediately upon first use to prevent "body stream already read"
      return cacheEntry.promise;
    }

    // Fallback if not pre-computed handled by component
    return null;
  }
};
