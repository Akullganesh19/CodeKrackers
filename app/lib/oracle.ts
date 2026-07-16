// app/lib/oracle.ts

class PredictiveOracle {
  private predictiveCache: Record<string, Promise<Response>> = {};

  private getCacheKey(text: string): string {
    return text.trim();
  }

  public preComputeScan(text: string, token: string) {
    const key = this.getCacheKey(text);

    // Don't pre-compute if it's too short, empty, or already computing
    if (!key || key.length < 10) return;
    if (key in this.predictiveCache) return;

    console.log(`[Oracle] Pre-computing scan for: ${key.substring(0, 20)}...`);

    const scanPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).then(async (res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res;
    }).catch((err) => {
      console.warn('[Oracle] Pre-computation failed:', err);
      // Clean up failed predictions
      delete this.predictiveCache[key];
      // Return a graceful fallback response to allow manual retries
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    this.predictiveCache[key] = scanPromise;
  }

  public async getScanResult(text: string, token: string): Promise<Response> {
    const key = this.getCacheKey(text);

    if (key in this.predictiveCache) {
      console.log(`[Oracle] Cache HIT! Zero-latency response for: ${key.substring(0, 20)}...`);
      const cachedPromise = this.predictiveCache[key];
      // Remove from cache to prevent "body stream already read" if reused
      delete this.predictiveCache[key];
      const response = await cachedPromise;
      return response.clone();
    }

    console.log(`[Oracle] Cache MISS. Fetching normally for: ${key.substring(0, 20)}...`);
    return fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    });
  }
}

export const Oracle = new PredictiveOracle();
