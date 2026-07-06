// 🔮 Oracle Engine: Predictive Intelligence
// Anticipates user behavior to eliminate latency.

type PredictionState = {
  promise: Promise<Response>;
  timestamp: number;
};

// Global cache for predictive fetches
const predictionCache: Record<string, PredictionState> = {};
const TTL_MS = 10 * 60 * 1000; // 10 minutes

export const oracle = {
  /**
   * Pre-computes an expensive API call in the background.
   * Useful when we know the user is about to request something (e.g. they finished typing an SMS).
   */
  preComputeScan: (text: string, token: string | null) => {
    if (!text || text.trim().length < 10) return;

    const cacheKey = `scan:${text.trim()}`;
    if (predictionCache[cacheKey] !== undefined) return; // Already predicting

    console.log(`[Oracle] 🔮 Predicting user will scan SMS, pre-computing...`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`,
      },
      body: JSON.stringify({ text }),
    }).then(res => res.clone()).catch(err => {
      // Degrade gracefully on prediction failure by returning a 500 response
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    predictionCache[cacheKey] = {
      promise,
      timestamp: Date.now(),
    };
  },

  /**
   * Resolves a prediction if it exists, otherwise returns null so the caller can fall back.
   * Important: always clones the response to prevent "body already read" errors.
   */
  resolvePrediction: async (text: string): Promise<Response | null> => {
    const cacheKey = `scan:${text.trim()}`;
    const prediction = predictionCache[cacheKey];

    if (prediction !== undefined) {
      if (Date.now() - prediction.timestamp < TTL_MS) {
        console.log(`[Oracle] ⚡ Prediction hit for SMS scan. Zero latency!`);
        // Remove from cache to free memory and ensure fresh fetch next time if needed
        delete predictionCache[cacheKey];
        return (await prediction.promise).clone();
      } else {
        // Expired
        delete predictionCache[cacheKey];
      }
    }

    return null;
  }
};
