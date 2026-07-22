export const predictiveCache: Record<string, Promise<any>> = {};
const MAX_CACHE_SIZE = 10;

export const Oracle = {
  preComputeScan: (text: string, token: string) => {
    if (!text || text.length < 5) return;

    // Eviction policy
    const keys = Object.keys(predictiveCache);
    if (keys.length >= MAX_CACHE_SIZE) {
      delete predictiveCache[keys[0]];
    }

    const key = text.trim();
    if (key in predictiveCache) return;

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).then(res => {
      if (!res.ok) {
        throw new Error('Scan failed');
      }
      return res.json();
    }).catch(err => {
      delete predictiveCache[key];
      throw err;
    });

    predictiveCache[key] = promise;

    // Attach a silent catch to prevent UnhandledPromiseRejectionWarning
    // when the promise is not awaited anywhere else.
    promise.catch(() => {});
  },

  getScanResult: async (text: string, token: string) => {
    const key = text.trim();
    if (key in predictiveCache) {
      try {
        const result = await predictiveCache[key];
        // Remove from cache after successful consumption if needed,
        // or let it stay for repeated clicks. We'll leave it for now.
        return result;
      } catch (err) {
        // Fallback to manual request if cached failed
        // It was already deleted from cache in preComputeScan catch
      }
    }

    // Normal request if not cached
    const res = await fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    });
    if (!res.ok) throw new Error('Scan failed');
    return res.json();
  }
};
