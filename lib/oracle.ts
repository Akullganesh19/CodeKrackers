// 🛸 Oracle: Predictive Intelligence Engine
// Intercepts and caches backend fetches based on likely user behavior.

export class OracleEngine {
  private cache: Record<string, Promise<Response>> = {};

  /**
   * Generates a cache key based on the URL, text body, and optional headers (like Authorization).
   */
  private getCacheKey(endpoint: string, text: string, headers?: Record<string, string>): string {
    const auth = headers?.Authorization || 'no-auth';
    return `${endpoint}|${text}|${auth}`;
  }

  /**
   * Starts a fetch request in the background and caches its Promise.
   * Useful when we anticipate the user is going to hit 'Analyze'.
   */
  public preComputeScan(endpoint: string, text: string, headers?: Record<string, string>) {
    if (!text.trim()) return;

    const key = this.getCacheKey(endpoint, text, headers);

    // Don't re-trigger if it's already in flight or cached
    if (key in this.cache) return;

    console.log(`[Oracle] 🛸 Pre-computing scan for: ${text.substring(0, 20)}...`);

    const promise = fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ text })
    });

    this.cache[key] = promise;
  }

  /**
   * Retrieves the cached fetch Promise if it exists.
   * If the fetch failed or isn't ok, it evicts the cache and returns null
   * so the consumer can fallback to a native fetch.
   */
  public async getScanResult(endpoint: string, text: string, headers?: Record<string, string>): Promise<Response | null> {
    const key = this.getCacheKey(endpoint, text, headers);
    const cachedPromise = this.cache[key];

    if (cachedPromise) {
      console.log(`[Oracle] 🛸 Cache hit! Returning pre-computed result.`);
      try {
        const response = await cachedPromise;
        // We need to clone the response because the body can only be consumed once
        const clonedResponse = response.clone();

        if (!clonedResponse.ok) {
          console.warn(`[Oracle] 🛸 Pre-computed fetch returned non-ok status: ${clonedResponse.status}. Evicting cache.`);
          delete this.cache[key];
          return null;
        }

        return clonedResponse;
      } catch (error) {
        console.error(`[Oracle] 🛸 Pre-computed fetch failed. Evicting cache.`, error);
        delete this.cache[key];
        return null;
      }
    }

    console.log(`[Oracle] 🛸 Cache miss. Proceeding with standard fetch.`);
    return null;
  }
}

export const oracle = new OracleEngine();
