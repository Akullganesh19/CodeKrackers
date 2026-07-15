export const Oracle = {
  // Cache of predictive fetch Promises
  predictiveCache: {} as Record<string, Promise<Response>>,

  preComputeScan: (text: string, token: string) => {
    const key = text.trim();
    // Only predict if the user has typed a meaningful amount of text
    if (!key || key.length < 10) return;

    if (key in Oracle.predictiveCache) return; // Already computing/computed

    // Start background fetch and store the promise
    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res;
    }).catch(err => {
      // On error, remove from cache so a manual retry will do a fresh fetch
      delete Oracle.predictiveCache[key];
      throw err;
    });

    Oracle.predictiveCache[key] = fetchPromise;
  },

  getScanResult: async (text: string, token: string): Promise<Response> => {
    const key = text.trim();

    if (key in Oracle.predictiveCache) {
      // Consume the cached prediction
      const promise = Oracle.predictiveCache[key];
      delete Oracle.predictiveCache[key]; // Consume once to prevent "body stream already read"

      try {
        const response = await promise;
        return response.clone();
      } catch (err) {
        // If the precomputed promise failed, fall through to a normal fetch
        console.warn('Predicted fetch failed, falling back to manual fetch', err);
      }
    }

    // Normal fallback fetch
    return fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    });
  }
};
