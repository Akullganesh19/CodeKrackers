'use client'

let isInitialized = false;

// We initialize outside of React's lifecycle to ensure it runs before any child components mount and fire their own fetch effects.
if (typeof window !== 'undefined' && !isInitialized) {
  isInitialized = true;

  const originalFetch = window.fetch;
  const inFlightRequests = new Map<string, Promise<Response>>();

  const customFetch = async function (input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    // Extract URL and Method
    let url = '';
    let method = 'GET';
    let reqHeaders: Record<string, string> = {};

    if (typeof input === 'string') {
      url = input;
    } else if (input instanceof URL) {
      url = input.toString();
    } else if (input instanceof Request) {
      url = input.url;
      method = input.method;
      input.headers.forEach((value, key) => { reqHeaders[key] = value; });
    }

    if (init && init.method) {
      method = init.method.toUpperCase();
    }

    if (init && init.headers) {
       const h = init.headers;
       if (h instanceof Headers) {
         h.forEach((value, key) => { reqHeaders[key] = value; });
       } else if (Array.isArray(h)) {
         h.forEach(([key, value]) => { reqHeaders[key] = value; });
       } else {
         Object.assign(reqHeaders, h);
       }
    }

    // Only coalesce GET requests without AbortSignal for now to keep it safe
    // (Handling AbortSignal properly in a shared promise requires tracking multiple signals)
    const hasSignal = (init && init.signal) || (input instanceof Request && input.signal);

    if (method !== 'GET' || hasSignal) {
      return originalFetch(input, init);
    }

    // Create a cache key based on URL and headers
    // Sort header keys to ensure consistent JSON stringification
    const sortedHeaders: Record<string, string> = {};
    Object.keys(reqHeaders).sort().forEach(k => {
       sortedHeaders[k] = reqHeaders[k];
    });
    const headersStr = JSON.stringify(sortedHeaders);
    const cacheKey = `${url}::${headersStr}`;

    if (inFlightRequests.has(cacheKey)) {
      // console.log(`🌀 Phantom: Coalesced request for ${url}`);
      const promise = inFlightRequests.get(cacheKey)!;

      // We must clone the response because the body stream can only be read once
      return promise.then(res => res.clone());
    }

    const promise = originalFetch(input, init).finally(() => {
      inFlightRequests.delete(cacheKey);
    });

    inFlightRequests.set(cacheKey, promise);

    return promise.then(res => res.clone());
  };

  // Assign using defineProperty to bypass strict TypeScript/React-Hooks immutability checks on global objects
  Object.defineProperty(window, 'fetch', {
    value: customFetch,
    writable: true,
    configurable: true
  });
}

export function FetchInterceptor({ children }: { children: React.ReactNode }) {
  // Setup is done synchronously at module level now, just render children
  return <>{children}</>
}
