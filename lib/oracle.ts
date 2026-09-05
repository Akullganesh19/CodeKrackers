/**
 * 🔮 Oracle Predictive Engine
 *
 * Capability: Precomputes API responses before the user asks for them.
 * How it works: Intercepts likely actions (like analyzing SMS text) while the user
 * is still typing or paused, fetching the result into a hidden cache. When the user
 * actually clicks the button, the response is delivered instantly.
 */

const PREDICTION_CACHE = new Map<string, Promise<unknown>>();
const CACHE_TIMESTAMP = new Map<string, number>();
const TTL_MS = 1000 * 60; // 1 minute TTL

// Use the URL as the debounce key so all typing for a given endpoint shares a timer
const DEBOUNCE_TIMERS = new Map<string, NodeJS.Timeout>();

function cleanCache() {
  const now = Date.now();
  for (const [key, timestamp] of CACHE_TIMESTAMP.entries()) {
    if (now - timestamp > TTL_MS) {
      PREDICTION_CACHE.delete(key);
      CACHE_TIMESTAMP.delete(key);
    }
  }
}

export const Oracle = {
  /**
   * Predictively fires an API request if the user seems likely to execute it.
   */
  preComputeScan: (
    url: string,
    text: string,
    headers?: Record<string, string>,
    keyOverride?: string
  ) => {
    cleanCache();

    if (!text || text.trim().length < 10) return; // Too short to predict

    const cacheKey = keyOverride || text.trim();

    if (PREDICTION_CACHE.has(cacheKey)) {
      return; // Already predicted or predicting
    }

    // Debounce: don't predict while they are actively typing fast
    if (DEBOUNCE_TIMERS.has(url)) {
      clearTimeout(DEBOUNCE_TIMERS.get(url)!);
    }

    const timer = setTimeout(() => {
      console.log(`[🔮 Oracle] Predicting future user action for text: "${text.substring(0, 15)}..."`);

      const fetchPromise = fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(headers || {})
        },
        body: JSON.stringify({ text: cacheKey })
      })
      .then(res => {
        if (!res.ok) throw new Error(`Oracle Fetch Error: ${res.status}`);
        // We clone so the actual consumer can read the stream
        const clone = res.clone();
        return clone.json();
      })
      .catch((err) => {
        console.error('[🔮 Oracle] Prediction failed:', err);
        PREDICTION_CACHE.delete(cacheKey);
        CACHE_TIMESTAMP.delete(cacheKey);
        // We throw so if the user clicks while the promise is in flight, the consumer gets the error
        throw err;
      });

      // To avoid unhandled promise rejection in the global scope if the user NEVER asks for it:
      fetchPromise.catch(() => {}); // Dummy catch for unhandled rejection

      PREDICTION_CACHE.set(cacheKey, fetchPromise);
      CACHE_TIMESTAMP.set(cacheKey, Date.now());
      DEBOUNCE_TIMERS.delete(url);
    }, 600); // Wait 600ms after last keystroke to predict

    DEBOUNCE_TIMERS.set(url, timer);
  },

  /**
   * Resolves the precomputed scan, or falls back to actual fetching.
   */
  getScanResult: async (
    url: string,
    text: string,
    headers?: Record<string, string>,
    keyOverride?: string
  ): Promise<unknown> => {
    cleanCache();

    const cacheKey = keyOverride || text.trim();

    if (PREDICTION_CACHE.has(cacheKey)) {
      console.log(`[🔮 Oracle] ⚡ Zero-latency prediction hit for: "${text.substring(0, 15)}..."`);
      const promise = PREDICTION_CACHE.get(cacheKey)!;
      try {
        return await promise;
      } catch (err) {
        // Fallback on error
        console.log(`[🔮 Oracle] Prediction previously failed, refetching:`, err);
      }
    } else {
      console.log(`[🔮 Oracle] Miss - user was faster than prediction or text was too short.`);
    }

    // Fallback: standard fetch
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {})
      },
      body: JSON.stringify({ text: cacheKey })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText);
    }

    return response.json();
  }
};
