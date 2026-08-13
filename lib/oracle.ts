class PredictiveOracle {
  private scanCache: Record<string, Promise<unknown | null>> = {};
  private MAX_CACHE_SIZE = 10;

  private evictIfNecessary() {
    const keys = Object.keys(this.scanCache);
    if (keys.length > this.MAX_CACHE_SIZE) {
      delete this.scanCache[keys[0]];
    }
  }

  public preComputeScan(text: string, token: string | null) {
    if (!text || text.length < 15) return;

    // Normalize key to lower to catch slight variations
    const key = text.trim();

    if (key in this.scanCache) return;

    this.evictIfNecessary();

    // Start background fetch and cache the promise
    this.scanCache[key] = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    })
    .then(res => {
      if (!res.ok) throw new Error(`Status: ${res.status}`);
      return res.json();
    })
    .catch(err => {
      console.error('Oracle prediction failed:', err);
      delete this.scanCache[key]; // Evict on failure to allow retry
      return null; // Return null so app doesn't crash on unhandled rejection
    });
  }

  public async getScanResult(text: string, token: string | null): Promise<unknown> {
    const key = text.trim();

    if (key in this.scanCache) {
      const cachedResult = await this.scanCache[key];
      if (cachedResult !== null) {
        console.log('Oracle: Served prediction from cache');
        return cachedResult;
      }
    }

    console.log('Oracle: Cache miss or previous failure, running native fetch');
    const response = await fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText);
    }

    return response.json();
  }
}

export const oracle = new PredictiveOracle();
