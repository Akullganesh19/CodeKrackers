/**
 * 🛸 Oracle - Predictive Intelligence Engine
 *
 * Anticipates user actions and pre-computes API requests before the user
 * explicitly triggers them, delivering a zero-latency experience.
 */

const cache: Record<string, Promise<Response>> = {};
const debounceTimers: Record<string, ReturnType<typeof setTimeout>> = {};

export const Oracle = {
  preComputeScan(url: string, options: { headers?: Record<string, string>, body?: string, keyOverride?: string } = {}) {
    const timerKey = url;
    const { body, headers, keyOverride } = options;
    const debounceMs = 400;

    if (timerKey in debounceTimers) {
      clearTimeout(debounceTimers[timerKey]);
    }

    debounceTimers[timerKey] = setTimeout(() => {
      const cacheKey = keyOverride || (body ? `${url}|${body}` : url);

      if (cacheKey in cache) return;

      // Cleanup previous pending fetches for the same url to avoid memory leak
      // from intermediate states.
      Object.keys(cache).forEach(k => {
          if (k.startsWith(url + "|") && k !== cacheKey) {
             delete cache[k]
          }
      });

      const promise = fetch(url, {
        method: body ? 'POST' : 'GET',
        headers: headers,
        body: body
      });

      cache[cacheKey] = promise;

      promise.catch(() => {
        if (cacheKey in cache && cache[cacheKey] === promise) {
          delete cache[cacheKey];
        }
      });
    }, debounceMs);
  },

  getScanResult(url: string, options: { body?: string, keyOverride?: string } = {}): Promise<Response> | null {
    const cacheKey = options.keyOverride || (options.body ? `${url}|${options.body}` : url);
    if (cacheKey in cache) {
      const promise = cache[cacheKey];
      delete cache[cacheKey];
      return promise;
    }
    return null;
  }
};
