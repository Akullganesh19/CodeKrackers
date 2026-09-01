/**
 * 🔮 Oracle: Predictive Intelligence Engine
 * Predicts and pre-computes API responses before the user asks for them.
 */

type CacheEntry = {
  promise: Promise<unknown>;
  timestamp: number;
};

class PredictionEngine {
  public cache: Record<string, CacheEntry> = {};
  private debounceTimer: NodeJS.Timeout | null = null;

  public preComputeScan(text: string, headers: HeadersInit = {}) {
    if (!text || text.length < 10) return; // Need enough context

    const key = `scan_${text}`;
    if (this.cache[key]) return; // Already computing/computed

    this.cleanup();

    console.log(`[Oracle] 🔮 Pre-computing scan for text...`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ text })
    })
    .then(async res => {
      if (!res.ok) throw new Error('Prediction fetch failed');
      return res.json();
    })
    .catch(err => {
      console.warn('[Oracle] 🔮 Prediction failed, evicting cache', err);
      delete this.cache[key];
      return null;
    });

    this.cache[key] = {
      promise,
      timestamp: Date.now()
    };
  }

  public predictNextScan(text: string, headers: HeadersInit = {}) {
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.preComputeScan(text, headers);
    }, 500); // Wait for user to pause typing
  }

  public getCachedResult(text: string): Promise<unknown> | null {
    const key = `scan_${text}`;
    const cached = this.cache[key];

    if (cached) {
      console.log(`[Oracle] 🔮 Cache hit! Delivering zero-latency prediction.`);
      return cached.promise;
    }
    return null;
  }

  private cleanup() {
    const now = Date.now();
    for (const key in this.cache) {
      // 5 min TTL
      if (now - this.cache[key].timestamp > 5 * 60 * 1000) {
        delete this.cache[key];
      }
    }
  }
}

export const oracle = new PredictionEngine();
