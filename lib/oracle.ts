// lib/oracle.ts
// Predictive intelligence module

type CacheKey = string;
type FetchPromise = Promise<Response | null>;

class OracleEngine {
  private cache: Record<CacheKey, { promise: FetchPromise, timestamp: number }> = {};
  private readonly TTL_MS = 60000; // 60 seconds

  preComputeScan(url: string, body: Record<string, unknown>, headers?: Record<string, string>): void {
    const key = JSON.stringify({ url, body });

    // Evict old cache if it exists
    if (key in this.cache) {
      if (Date.now() - this.cache[key].timestamp > this.TTL_MS) {
        delete this.cache[key];
      } else {
        return; // valid cache hit
      }
    }

    console.log(`[Oracle] Pre-computing scan for ${url}`);

    // Start the fetch but don't await it here. Store the promise.
    const promise = fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {})
      },
      body: JSON.stringify(body)
    }).catch(err => {
      console.error(`[Oracle] Pre-compute failed for ${url}:`, err);
      // On failure, evict from cache to allow normal retry
      delete this.cache[key];
      return null;
    });

    this.cache[key] = { promise, timestamp: Date.now() };
  }

  async getScanResult(url: string, body: Record<string, unknown>, headers?: Record<string, string>): Promise<Response> {
    const key = JSON.stringify({ url, body });

    if (key in this.cache) {
      if (Date.now() - this.cache[key].timestamp <= this.TTL_MS) {
        console.log(`[Oracle] Cache hit for ${url}`);
        const res = await this.cache[key].promise;
        if (res) {
          // Clone the response so it can be consumed
          return res.clone();
        }
      } else {
         delete this.cache[key]; // Expired
      }
    }

    console.log(`[Oracle] Cache miss for ${url}, fetching normally`);
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {})
      },
      body: JSON.stringify(body)
    });
  }
}

export const oracle = new OracleEngine();
