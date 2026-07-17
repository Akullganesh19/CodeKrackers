// Oracle Predictive Engine
// Anticipates user behavior by pre-computing expensive API requests
// before the user explicitly requests them, achieving zero-latency UI.

const preComputeCache: Record<string, Promise<Response>> = {};

export const Oracle = {
  /**
   * Pre-computes an API scan. Designed to be called when user interaction
   * indicates they might request a scan soon (e.g. while typing).
   */
  preComputeScan: (text: string, token: string | null): void => {
    const key = text.trim();
    if (!key || key.length < 5) return;

    // If we're already computing this exact text, skip
    if (key in preComputeCache) return;

    console.log("🔮 Oracle: Pre-computing scan for:", key.substring(0, 20) + "...");

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text: key })
    }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res;
    }).catch(err => {
      console.error("🔮 Oracle: Prediction failed.", err);
      // Delete the failed entry from the cache
      delete preComputeCache[key];
      // Return a graceful fallback response
      return new Response(JSON.stringify({ error: "precompute failed" }), { status: 500 });
    });

    preComputeCache[key] = promise;
  },

  /**
   * Retrieves the scan result, either returning the pre-computed promise
   * or initiating a new fetch if the cache missed.
   */
  getScanResult: async (text: string, token: string | null): Promise<Response> => {
    const key = text.trim();

    if (key in preComputeCache) {
      console.log("🔮 Oracle: Cache hit! Zero latency engaged.");
      const response = await preComputeCache[key];
      // Ensure the cache entry is deleted immediately upon first use
      delete preComputeCache[key];

      if (response.ok) {
        return response.clone();
      }
      // If the precomputed response failed, we fallback to a normal fetch
    } else {
      console.log("🔮 Oracle: Cache miss. Normal fetch.");
    }

    return fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text: key })
    });
  }
};
