// app/lib/oracle.ts

/**
 * 🛸 Oracle Predictive Engine
 *
 * Predicts user intent and pre-computes expensive operations (like AI text scanning)
 * before the user explicitly asks for them, enabling seamless zero-latency experiences.
 */

type CacheKey = string;
type ScanPromise = Promise<Response>;

class OracleEngine {
  private cache: Record<CacheKey, ScanPromise> = {};
  private cacheTimestamps: Record<CacheKey, number> = {};
  private MAX_AGE = 1000 * 60 * 5; // 5 minutes TTL

  private cleanup() {
    const now = Date.now();
    for (const key in this.cacheTimestamps) {
      if (now - this.cacheTimestamps[key] > this.MAX_AGE) {
        delete this.cache[key];
        delete this.cacheTimestamps[key];
      }
    }
  }

  /**
   * Pre-computes scan result by caching unresolved client-side API fetch Promises.
   */
  preComputeScan(text: string, token: string): void {
    this.cleanup();
    const key = text.trim();
    if (!key || key.length < 10) return;

    // Use `in` operator to safely check for key existence without type errors on truthiness
    if (key in this.cache) return;

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).then(res => {
      // Explicitly check for !res.ok to catch HTTP errors, as fetch only rejects on network failure
      if (!res.ok) {
        throw new Error(`HTTP Error: ${res.status}`);
      }
      return res;
    }).catch(err => {
      // Always delete the failed entry from the cache
      delete this.cache[key];
      // Graceful fallback response so the promise still resolves to a Response object
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    this.cache[key] = promise;
    this.cacheTimestamps[key] = Date.now();
  }

  /**
   * Retrieves the pre-computed scan result if available.
   */
  async getScanResult(text: string): Promise<Response | undefined> {
    const key = text.trim();
    if (key in this.cache) {
      const res = await this.cache[key];
      // Always delete cache entry after first use to avoid "body stream already read" if consumed again
      delete this.cache[key];
      return res.clone();
    }
    return undefined;
  }
}

export const Oracle = new OracleEngine();
