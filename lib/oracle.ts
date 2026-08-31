/**
 * 🛸 Oracle - Predictive Intelligence Cache
 * Pre-computes and caches API responses based on likely user actions.
 */
class OracleEngine {
  // Maps a unique cache key (like text content) to an inflight/resolved fetch Promise
  private cache: Record<string, Promise<Response | null>> = {};

  /**
   * Pre-computes the result of a scan by firing the request before the user clicks.
   */
  preComputeScan(text: string, headers: Record<string, string>): void {
    if (!text || text.trim().length === 0) return;

    // We only want to precompute if we don't already have it in flight
    if (this.cache[text]) return;

    console.log(`[Oracle] Pre-computing scan for: "${text.substring(0, 20)}..."`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ text })
    }).catch(err => {
      console.warn(`[Oracle] Pre-compute failed, evicting cache for text:`, text, err);
      // Evict on failure so the actual click gracefully falls back to a fresh fetch
      delete this.cache[text];
      return null;
    });

    this.cache[text] = promise;
  }

  /**
   * Retrieves the pre-computed fetch Promise if it exists.
   */
  getScanResult(text: string): Promise<Response | null> | null {
    if (!text) return null;
    return this.cache[text] || null;
  }
}

export const Oracle = new OracleEngine();
