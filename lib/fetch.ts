const inFlight = new Map<string, Promise<Response>>();

export function setupFetchInterceptor() {
  if (typeof window === 'undefined') return;

  // Prevent multiple initializations
  if ((window as any).__fetchIntercepted) return;
  (window as any).__fetchIntercepted = true;

  const originalFetch = window.fetch;

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit) {
    let method = 'GET';
    if (init && init.method) {
      method = init.method.toUpperCase();
    } else if (input instanceof Request) {
      method = input.method.toUpperCase();
    }

    // Only coalesce GET requests
    if (method !== 'GET') {
      return originalFetch.call(this, input, init);
    }

    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : (input as Request).url;

    if (inFlight.has(url)) {
      console.debug(`[Phantom] Coalesced duplicate GET request to: ${url}`);
      const res = await inFlight.get(url)!;
      return res.clone();
    }

    const promise = originalFetch.call(this, input, init);

    inFlight.set(url, promise);

    try {
      const res = await promise;
      return res.clone();
    } finally {
      // We use a small timeout before deleting to allow simultaneous microtasks to catch the promise
      setTimeout(() => inFlight.delete(url), 50);
    }
  };
}
