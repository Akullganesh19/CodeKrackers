class OracleEngine {
  private cache: Record<string, Promise<unknown>> = {};

  preComputeScan(url: string, options: { method?: string; headers?: Record<string, string>; body?: string, keyOverride?: string } = {}) {
    const key = options.keyOverride || url + (options.body || '');

    if (key in this.cache) {
      return this.cache[key];
    }

    const fetchPromise = fetch(url, options)
      .then(async (res) => {
        if (!res.ok) {
          throw new Error('Prefetch failed');
        }
        return res.json();
      })
      .catch((err) => {
        console.warn('Oracle prediction failed:', err);
        delete this.cache[key];
        return null;
      });

    this.cache[key] = fetchPromise;
    return fetchPromise;
  }

  getScanResult(url: string, bodyStr: string = '', keyOverride?: string) {
    const key = keyOverride || url + bodyStr;
    return this.cache[key] || null;
  }
}

export const oracle = new OracleEngine();
