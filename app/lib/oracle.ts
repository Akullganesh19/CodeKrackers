// Predictive Intelligence Engine (Oracle)

type CachedPrediction = {
  promise: Promise<Response>;
  timestamp: number;
};

// Global cache to persist across components
const predictionCache: Record<string, CachedPrediction | undefined> = {};
const DEFAULT_TTL = 30000; // 30 seconds

export const Oracle = {
  /**
   * Pre-computes a scan for text input.
   * Useful when user is pasting/typing but hasn't clicked "Analyze" yet.
   */
  preComputeScan: (text: string, endpoint: string) => {
    if (!text || text.length < 15) return;
    const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null;
    if (!token) return; // Never prefetch without auth

    const key = `${endpoint}-${text}`;

    if (predictionCache[key] !== undefined) {
      const cached = predictionCache[key] as CachedPrediction;
      if (Date.now() - cached.timestamp < DEFAULT_TTL) {
        return; // Already pre-computing
      }
    }

    const payload = endpoint.includes('scan-voice') ? { transcript: text } : { text };

    // Fire background fetch and cache the promise
    const p = fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    }).catch(err => {
      // Graceful degradation: remove from cache on failure so manual retry attempts fresh fetch
      delete predictionCache[key];
      // Return a fallback response so awaited promise doesn't throw unhandled rejection
      return new Response(JSON.stringify({
        isScam: false,
        confidence: 0,
        riskFactors: [],
        recommendation: "Prediction failed",
        tags: []
      }), { status: 500 });
    });

    predictionCache[key] = { promise: p, timestamp: Date.now() };
  },

  /**
   * Resolves a prediction, cloning the response to allow multiple reads.
   */
  resolvePrediction: async (text: string, endpoint: string): Promise<Response | null> => {
    const key = `${endpoint}-${text}`;
    if (predictionCache[key] !== undefined) {
      const cached = predictionCache[key] as CachedPrediction;
      if (Date.now() - cached.timestamp < DEFAULT_TTL) {
        const res = await cached.promise;
        return res.clone();
      }
    }
    return null; // Cache miss or expired
  },

  /**
   * Prefetch route data (e.g. when hovering over a link)
   */
  prefetchRouteData: (route: string, fetchFn: () => Promise<Response>) => {
    if (predictionCache[route] !== undefined) {
      const cached = predictionCache[route] as CachedPrediction;
      if (Date.now() - cached.timestamp < DEFAULT_TTL) {
        return;
      }
    }

    const p = fetchFn().catch(err => {
      return new Response(JSON.stringify({ error: "Prefetch failed" }), { status: 500 });
    });

    predictionCache[route] = { promise: p, timestamp: Date.now() };
  }
};
