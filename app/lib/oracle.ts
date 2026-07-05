// Oracle - Predictive Intelligence Engine

/**
 * Caches pending and resolved predictions globally
 */
const predictionCache: Record<string, Promise<any> | any> = {};

/**
 * Route dependencies that can be prefetched
 */
const routeDependencies: Record<string, string[]> = {
  '/dashboard': ['/api/analytics/dashboard-summary'],
  '/analytics': ['/api/analytics/dashboard-summary', '/api/analytics/threat_map'],
};

export const Oracle = {
  /**
   * Pre-computes a scan for a given text by issuing the API call early.
   * If the text changes significantly, a new prediction is spawned.
   */
  preComputeScan: async (text: string, token: string | null) => {
    if (!text || text.length < 15) return;

    // Hash or simply use the text as a key for this simple implementation
    const key = `scan_${text.substring(0, 50).trim()}`;

    if (predictionCache[key] !== undefined) return; // Already predicting this

    // Immediately store the promise in the cache
    predictionCache[key] = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    })
      .then(res => {
        if (!res.ok) throw new Error('Prediction failed');
        // We clone here just in case, though Next's fetch might handle it
        return res.clone().json();
      })
      .catch(err => {
        // Silently fail the prediction so normal flow takes over
        delete predictionCache[key];
        return null;
      });
  },

  /**
   * Resolves a prediction for a given text, if one exists.
   * Otherwise returns null so the caller can fall back to normal fetch.
   */
  resolvePrediction: async (text: string): Promise<any | null> => {
    const key = `scan_${text.substring(0, 50).trim()}`;
    if (predictionCache[key] !== undefined) {
      const data = await predictionCache[key];
      // Clean up to prevent huge memory leak, though LRU would be better
      delete predictionCache[key];
      return data;
    }
    return null;
  },

  /**
   * Prefetches necessary data for a route based on intent (e.g. hover).
   */
  prefetchRouteData: (route: string, token: string | null) => {
    const urlsToFetch = routeDependencies[route];
    if (!urlsToFetch) return;

    urlsToFetch.forEach(url => {
      const key = `route_${url}`;
      if (predictionCache[key] !== undefined) return;

      predictionCache[key] = fetch(`http://localhost:8000${url}`, {
        headers: {
          'Authorization': `Bearer ${token || 'dummy_token'}`
        }
      })
      .then(res => {
         if (!res.ok) throw new Error('Prefetch failed');
         // Store the clone so it can be consumed later
         return res.clone();
      })
      .catch(err => {
         delete predictionCache[key];
         return null;
      });
    });
  },

  /**
   * Tries to get the cached route response to avoid a network round trip.
   */
  resolveRouteData: async (url: string): Promise<Response | null> => {
    const key = `route_${url}`;
    if (predictionCache[key] !== undefined) {
      const res = await predictionCache[key];
      // We don't delete immediately so multiple components can use the prefetch
      // In a real app we'd have a TTL. Let's delete after 5 seconds here for simplicity.
      setTimeout(() => {
        delete predictionCache[key];
      }, 5000);
      return res ? res.clone() : null;
    }
    return null;
  }
};
