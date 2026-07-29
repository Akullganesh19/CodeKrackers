// app/lib/oracle.ts

type CacheEntry = Promise<Response | null>;
const predictiveCache: Record<string, CacheEntry> = {};
const MAX_CACHE_SIZE = 10;

/**
 * The Oracle module provides predictive intelligence capabilities.
 * It anticipates user actions (like scanning an SMS) and pre-computes the results
 * in the background while the user is still interacting with the UI.
 */
export const Oracle = {
  /**
   * Pre-computes the scan result for a given text.
   * This is intended to be called debounced during user typing.
   */
  preComputeScan: (text: string) => {
    const trimmedText = text.trim();
    if (!trimmedText || trimmedText.length < 10) return; // Don't pre-compute for very short texts

    // If already in cache, skip
    if (trimmedText in predictiveCache) return;

    // Eviction policy: prevent unbounded memory growth
    const keys = Object.keys(predictiveCache);
    if (keys.length >= MAX_CACHE_SIZE) {
      const oldestKey = keys[0];
      delete predictiveCache[oldestKey];
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') || 'dummy_token' : 'dummy_token';

    // Start the background fetch and cache the promise
    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: trimmedText })
    }).then(response => {
      if (!response.ok) return null;
      // We must clone the response because the body can only be read once
      return response.clone();
    }).catch(err => {
      // Gracefully handle errors in the background promise
      console.warn('Oracle pre-computation failed:', err);
      return null;
    });

    predictiveCache[trimmedText] = fetchPromise;
  },

  /**
   * Retrieves the pre-computed scan result, or fetches it if not available.
   * The cached promise is removed upon first read.
   */
  getScanResult: async (text: string): Promise<any | null> => {
    const trimmedText = text.trim();
    if (!trimmedText) return null;

    if (trimmedText in predictiveCache) {
      const cachedPromise = predictiveCache[trimmedText];
      // Immediately delete from cache so it's only used once (prevents double reading of body stream)
      delete predictiveCache[trimmedText];

      const response = await cachedPromise;
      if (response) {
        try {
          return await response.json();
        } catch (e) {
          console.warn('Oracle failed to parse cached response:', e);
          return null;
        }
      }
    }

    return null; // Return null if not in cache or if it failed, caller will fallback to normal fetch
  }
};
