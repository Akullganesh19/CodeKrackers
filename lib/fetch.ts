if (typeof window !== "undefined") {
  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async function (
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> {
    const method = init?.method?.toUpperCase() || "GET";

    // Only coalesce GET requests
    if (method !== "GET") {
      return originalFetch.apply(this, [input, init] as unknown as Parameters<typeof originalFetch>);
    }

    let urlStr = "";
    if (typeof input === "string") {
      urlStr = input;
    } else if (input instanceof URL) {
      urlStr = input.toString();
    } else if (input instanceof Request) {
      // For Request objects, we might also need to check method
      if (input.method.toUpperCase() !== "GET") {
        return originalFetch.apply(this, [input, init] as unknown as Parameters<typeof originalFetch>);
      }
      urlStr = input.url;
    }

    // Create a cache key using the URL
    // Note: This naive implementation ignores headers. For a robust implementation,
    // headers should be included in the cache key if they vary.
    const cacheKey = urlStr;

    if (inFlight.has(cacheKey)) {
      const promise = inFlight.get(cacheKey)!;
      // Clone response so multiple consumers can read the body stream
      return promise.then((res) => res.clone());
    }

    // Perform the actual fetch
    const fetchPromise = originalFetch.apply(this, [input, init] as unknown as Parameters<typeof originalFetch>);

    // We must ensure the promise in the map yields a Response that can be cloned.
    // The original response is consumed by the first caller if not careful.
    const sharedPromise = fetchPromise.then((res) => {
      // We resolve the shared promise with the original response,
      // and each subscriber will clone it.
      return res;
    });

    // Cleanup when done
    sharedPromise.finally(() => {
      inFlight.delete(cacheKey);
    });

    inFlight.set(cacheKey, sharedPromise);

    // First caller also gets a clone to preserve the shared response for others
    return sharedPromise.then(res => res.clone());
  };
}
