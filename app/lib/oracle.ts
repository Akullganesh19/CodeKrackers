export class Oracle {
  private static predictiveCache: Record<string, Promise<Response | null>> = {};
  private static MAX_CACHE_SIZE = 10;

  private static getCacheKey(text: string): string {
    return text.trim();
  }

  public static preComputeScan(text: string, token: string): void {
    const key = this.getCacheKey(text);
    if (!key) return;

    if (key in this.predictiveCache) return; // Already computing or computed

    // Enforce eviction policy
    const keys = Object.keys(this.predictiveCache);
    if (keys.length >= this.MAX_CACHE_SIZE) {
      delete this.predictiveCache[keys[0]]; // Evict oldest
    }

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    }).catch(error => {
      console.error('Oracle background fetch failed:', error);
      return null;
    });

    this.predictiveCache[key] = promise;
  }

  public static async getScanResult(text: string): Promise<Response | null> {
    const key = this.getCacheKey(text);
    if (!key) return null;

    const promise = this.predictiveCache[key];
    if (promise) {
      delete this.predictiveCache[key]; // Delete upon first use
      const response = await promise;
      if (response) {
        return response.clone();
      }
    }
    return null;
  }
}
