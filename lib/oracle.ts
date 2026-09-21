// Predictive Intelligence Engine (Oracle)
// Anticipates user actions and precomputes results

const predictionCache: Record<string, Promise<any>> = {};
const debounceTimers: Record<string, NodeJS.Timeout> = {};

export const Oracle = {
  /**
   * Precomputes an API response by triggering a fetch before the user explicitly requests it.
   * If the fetch is already running or completed, it uses the cached promise.
   */
  preComputeScan: (
    url: string,
    options?: {
      headers?: Record<string, string>,
      body?: string,
      keyOverride?: string
    }
  ) => {
    // Generate a unique key based on the URL and body to avoid returning stale/partial text results
    const key = options?.keyOverride || `${url}-${options?.body || ''}`;

    // Clear any existing debounce timer for this key/url base
    const baseKey = options?.keyOverride || url;
    if (debounceTimers[baseKey]) {
      clearTimeout(debounceTimers[baseKey]);
    }

    // Debounce the pre-compute to avoid spamming the backend during typing
    debounceTimers[baseKey] = setTimeout(() => {
      if (key in predictionCache) {
        return; // Already precomputing or cached for this exact payload
      }

      console.log(`[Oracle] 🔮 Predicting future need for: ${key}`);

      const fetchPromise = fetch(url, {
        method: options?.body ? 'POST' : 'GET',
        headers: options?.headers,
        body: options?.body,
      })
      .then(async res => {
        if (!res.ok) {
           const errorText = await res.text();
           throw new Error(`Server returned ${res.status}: ${errorText}`);
        }
        return await res.json();
      });

      // Cache the promise itself. Eventual callers can await it.
      // Attach a catch block *just for background cleanup* so it doesn't trigger Unhandled Rejection if unused.
      predictionCache[key] = fetchPromise;
      fetchPromise.catch(() => {
        delete predictionCache[key]; // Clean up failed predictions silently
      });

    }, 300); // 300ms debounce
  },

  /**
   * Retrieves a precomputed result if available, otherwise initiates a new fetch.
   */
  getScanResult: async (
    url: string,
    options?: {
      headers?: Record<string, string>,
      body?: string,
      keyOverride?: string
    }
  ) => {
    const key = options?.keyOverride || `${url}-${options?.body || ''}`;

    // If a prediction exists for this exact payload, use it!
    if (key in predictionCache) {
      console.log(`[Oracle] ⚡ Prediction Hit! Zero latency loading for: ${key}`);
      const cachedPromise = predictionCache[key];
      delete predictionCache[key]; // Clear cache after use
      return cachedPromise;
    }

    // Otherwise, fallback to normal fetch
    console.log(`[Oracle] 🐌 Prediction Miss. Normal loading for: ${key}`);
    const res = await fetch(url, {
      method: options?.body ? 'POST' : 'GET',
      headers: options?.headers,
      body: options?.body,
    });
    if (!res.ok) {
       const errorText = await res.text();
       throw new Error(`Server returned ${res.status}: ${errorText}`);
    }
    return await res.json();
  }
};
