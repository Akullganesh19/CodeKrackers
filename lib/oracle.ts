/**
 * 🛸 OracleEngine - Predictive Intelligence for VSDP
 * Anticipates user actions and pre-computes results for zero-latency experiences.
 */

class OracleEngine {
  private cache: Record<string, Promise<unknown>> = {};
  private timer: ReturnType<typeof setTimeout> | null = null;
  private debounceMs = 500;

  /**
   * Pre-computes the SMS scan when the user stops typing.
   * Caches the *promise* so `handleAnalyze` can await it directly.
   */
  public preComputeScan(text: string, headers?: HeadersInit) {
    // Clear any pending pre-computations
    if (this.timer) {
      clearTimeout(this.timer);
    }

    const trimmed = text.trim();
    if (!trimmed || trimmed.length < 10) return;

    this.timer = setTimeout(() => {
      console.log(`[Oracle 🛸] Pre-computing scan for: "${trimmed.substring(0, 20)}..."`);

      const p = fetch('http://localhost:8000/api/analytics/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify({ text: trimmed })
      }).then(async (res) => {
        if (!res.ok) {
           const err = await res.text();
           throw new Error(`Server Error (${res.status}): ${err}`);
        }
        return res.json();
      }).catch(err => {
        console.error(`[Oracle 🛸] Prediction failed:`, err);
        // Evict failed promise from cache gracefully
        delete this.cache[trimmed];
        return null;
      });

      this.cache[trimmed] = p;
    }, this.debounceMs);
  }

  /**
   * Returns the cached promise for a given text, or null if it wasn't pre-computed.
   */
  public getScanResult(text: string): Promise<unknown> | null {
    const trimmed = text.trim();
    if (this.cache[trimmed]) {
      console.log(`[Oracle 🛸] Zero-latency cache hit for: "${trimmed.substring(0, 20)}..."`);
      const p = this.cache[trimmed];
      // Clean up after consuming
      delete this.cache[trimmed];
      return p;
    }
    return null;
  }
}

export const oracle = new OracleEngine();
