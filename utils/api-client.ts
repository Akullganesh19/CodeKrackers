/**
 * Phantom Infrastructure: Request Coalescing Fetch Wrapper
 *
 * Intercepts duplicate simultaneous GET requests to the same URL
 * and coalesces them into a single network request.
 * Components unknowingly share the same promise and response body.
 */

const inFlight = new Map<string, Promise<Response>>();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type GlobalWindow = any;

export function setupPhantomFetch() {
  if (typeof window !== 'undefined' && !(window as GlobalWindow).__phantomFetchInitialized) {
    const originalFetch = window.fetch;

    window.fetch = async (...args) => {
      const input = args[0];
      const init = args[1];

      let method = 'GET';
      let urlStr = '';

      if (typeof input === 'string') {
        urlStr = input;
        method = (init?.method || 'GET').toUpperCase();
      } else if (input instanceof URL) {
        urlStr = input.toString();
        method = (init?.method || 'GET').toUpperCase();
      } else if (input instanceof Request) {
        urlStr = input.url;
        method = input.method.toUpperCase();
      }

      // Only coalesce GET requests
      if (method !== 'GET') {
        return originalFetch(...args);
      }

      const cacheKey = urlStr;

      if (inFlight.has(cacheKey)) {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('phantom-coalesced', { detail: { url: cacheKey } }));
        }
        const promise = inFlight.get(cacheKey)!;
        const res = await promise;
        return res.clone();
      }

      const promise = originalFetch(...args).finally(() => {
        inFlight.delete(cacheKey);
      });

      inFlight.set(cacheKey, promise);

      const res = await promise;
      return res.clone();
    };

    (window as GlobalWindow).__phantomFetchInitialized = true;
  }
}
