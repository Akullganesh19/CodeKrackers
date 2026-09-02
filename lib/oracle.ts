// lib/oracle.ts
// Oracle Predictive Intelligence Module

type CacheEntry = {
  promise: Promise<unknown>;
  timestamp: number;
};

class OraclePredictionEngine {
  private cache: Map<string, CacheEntry> = new Map();
  private ttl: number = 5 * 60 * 1000; // 5 minutes

  preComputeScan(url: string, headers?: HeadersInit, body?: string, keyOverride?: string) {
    const key = keyOverride || url;
    if (this.cache.has(key)) return;

    console.log(`🛸 Oracle: Pre-computing for key ${key.substring(0, 20)}...`);

    const promise = fetch(url, { method: body ? 'POST' : 'GET', headers, body })
      .then(res => {
        if (!res.ok) throw new Error("Pre-compute failed");
        return res.clone().json();
      })
      .catch(_err => {
        console.warn(`🛸 Oracle: Prediction failed for ${key.substring(0, 20)}...`);
        this.cache.delete(key);
        return null;
      });

    this.cache.set(key, { promise, timestamp: Date.now() });
  }

  async getScanResult(key: string): Promise<unknown | null> {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    console.log(`🛸 Oracle: Serving prediction for ${key.substring(0, 20)}...`);
    return entry.promise;
  }
}

export const oracle = new OraclePredictionEngine();
