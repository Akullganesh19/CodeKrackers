export const Oracle = {
  cache: {} as Record<string, Promise<unknown>>,
  debounceTimers: {} as Record<string, ReturnType<typeof setTimeout>>,

  preComputeScan: function(url: string, options?: { headers?: Record<string, string>, body?: unknown, keyOverride?: string, debounceMs?: number }) {
    const key = options?.keyOverride || url;

    if (key in this.debounceTimers) {
      clearTimeout(this.debounceTimers[key]);
    }

    const timer = setTimeout(() => {
      const fetchPromise = fetch(url, {
        method: options?.body ? 'POST' : 'GET',
        headers: options?.headers,
        body: options?.body ? JSON.stringify(options.body) : undefined
      }).then(async (res) => {
        if (!res.ok) throw new Error('API Error');
        return res.json();
      }).catch(() => {
        delete this.cache[key];
        return null; // Handle without throwing
      });

      this.cache[key] = fetchPromise;
      delete this.debounceTimers[key];
    }, options?.debounceMs || 500);

    this.debounceTimers[key] = timer;
  },

  getScanResult: function(url: string, keyOverride?: string): Promise<unknown> | null {
    const key = keyOverride || url;
    if (key in this.cache) {
      const promise = this.cache[key];
      delete this.cache[key];
      return promise;
    }
    return null;
  }
};
