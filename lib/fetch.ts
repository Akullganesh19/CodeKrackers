// Intelligent fetch interceptor with Request Coalescing
// This deduplicates simultaneous identical GET requests so components don't over-fetch.

const inFlight = new Map<string, Promise<Response>>();
const globalFetch = typeof window !== 'undefined' ? window.fetch : null;

export function initFetchInterceptor() {
  if (typeof window === 'undefined' || !globalFetch) return;

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit) {
    const method = init?.method?.toUpperCase() || (input instanceof Request ? input.method.toUpperCase() : 'GET');
    const isGet = method === 'GET';

    if (!isGet) {
      // Don't intercept mutations
      return globalFetch(input, init);
    }

    // Determine URL string
    let urlString = '';
    if (typeof input === 'string') {
      urlString = input;
    } else if (input instanceof URL) {
      urlString = input.toString();
    } else if (input instanceof Request) {
      urlString = input.url;
    }

    const cacheKey = `${method}:${urlString}`;

    // If an identical request is already in-flight, return its promise
    if (inFlight.has(cacheKey)) {
      return inFlight.get(cacheKey)!.then(res => res.clone());
    }

    // Otherwise, initiate the fetch and store the promise
    const promise = globalFetch(input, init).finally(() => {
      // Remove from map once settled
      inFlight.delete(cacheKey);
    });

    inFlight.set(cacheKey, promise);

    return promise.then(res => res.clone());
  };
}
