// Oracle Predictive Pre-computation Module
// Caches unresolved client-side API fetch Promises for seamless zero-latency user experiences

type CacheEntry = Promise<any>;

class PredictiveOracle {
  private cache: Record<string, CacheEntry> = {};
  private maxCacheSize = 20;

  private evictIfNecessary() {
    const keys = Object.keys(this.cache);
    if (keys.length > this.maxCacheSize) {
      // Delete the oldest entry
      const oldestKey = keys[0];
      if (oldestKey) {
        delete this.cache[oldestKey];
      }
    }
  }

  /**
   * Pre-computes the result of an API call in the background and stores the Promise.
   * Handles errors by returning null instead of throwing unhandled rejections.
   */
  public preComputeScan(text: string, token: string | null): void {
    if (!text.trim()) return;

    const cacheKey = text.trim();
    if (cacheKey in this.cache) return; // Already computing/computed

    this.evictIfNecessary();

    // Start background fetch and store the promise
    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    })
    .then(async (res) => {
      if (!res.ok) {
        delete this.cache[cacheKey]; // Evict on failure to allow retry
        return null;
      }
      return await res.json();
    })
    .catch((err) => {
      // Catch errors so unhandled rejections don't crash Next.js
      console.warn("Oracle pre-computation failed:", err);
      delete this.cache[cacheKey]; // Evict on failure to allow retry
      return null;
    });

    this.cache[cacheKey] = promise;
  }

  /**
   * Retrieves the cached Promise if available, otherwise returns null.
   */
  public getScanResult(text: string): CacheEntry | null {
    const cacheKey = text.trim();
    if (cacheKey in this.cache) {
      return this.cache[cacheKey];
    }
    return null;
  }
}

export const Oracle = new PredictiveOracle();
