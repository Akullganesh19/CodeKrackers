/**
 * 🛸 Oracle: Predictive Intelligence Engine
 *
 * The Oracle predicts user actions and pre-fetches/pre-computes data
 * before the user explicitly requests it. This eliminates perceived latency.
 */

interface PredictionEntry {
  promise: Promise<Response>;
  timestamp: number;
}

// Module-level cache to survive component unmounts
const PREDICTION_CACHE: Record<string, PredictionEntry> = {};
const TTL_MS = 1000 * 60 * 5; // 5 minutes

export const Oracle = {
  /**
   * Generates a cache key based on the text.
   */
  _getKey: (text: string) => {
    return text.trim().toLowerCase();
  },

  /**
   * Anticipates that a user will scan an SMS message and pre-computes the result.
   * Degrades gracefully if the request fails, allowing for a manual retry.
   */
  preComputeScan: (text: string, token: string) => {
    const key = Oracle._getKey(text);
    if (!key) return;

    // Check if already predicting/predicted
    const existing = PREDICTION_CACHE[key];
    if (existing && (Date.now() - existing.timestamp < TTL_MS)) {
      return;
    }

    // Start background prediction
    console.log(`🛸 Oracle: Pre-computing scan for text: "${text.substring(0, 20)}..."`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    })
    .then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res;
    })
    .catch(err => {
      // If the prediction fails or returns a non-ok status, delete it from the cache
      // so the user's explicit action will trigger a fresh network request.
      console.warn('🛸 Oracle: Prediction failed to compute, clearing from cache', err);
      delete PREDICTION_CACHE[key];
      // Return a graceful fallback 500 error response so we don't return undefined
      return new Response(JSON.stringify({ error: 'Prediction failed' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    PREDICTION_CACHE[key] = { promise, timestamp: Date.now() };
  },

  /**
   * Resolves a prediction if it exists, otherwise falls back to a normal fetch.
   */
  resolvePrediction: async (text: string, token: string): Promise<Response> => {
    const key = Oracle._getKey(text);
    const existing = PREDICTION_CACHE[key];

    if (existing && (Date.now() - existing.timestamp < TTL_MS)) {
      console.log(`🛸 Oracle: Resolving prediction instantly for text: "${text.substring(0, 20)}..."`);
      const response = await existing.promise;
      // ALWAYS clone the response to prevent "body stream already read" errors
      // if the response is accessed multiple times.
      return response.clone();
    }

    console.log(`🛸 Oracle: No valid prediction found, falling back to manual fetch.`);
    const response = await fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    });

    // Store in cache for future identical requests
    PREDICTION_CACHE[key] = { promise: Promise.resolve(response.clone()), timestamp: Date.now() };
    return response;
  },

  /**
   * Predictive prefetching for routes (example placeholder).
   */
  prefetchRouteData: (route: string) => {
     // implementation for route prefetch
  }
};
