"use client";

if (typeof window !== "undefined" && !((window as unknown) as { _fetchIntercepted: boolean; fetch: typeof fetch })._fetchIntercepted) {
  ((window as unknown) as { _fetchIntercepted: boolean; fetch: typeof fetch })._fetchIntercepted = true;
  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    let method = "GET";
    if (init && init.method) {
      method = init.method.toUpperCase();
    } else if (input instanceof Request) {
      method = input.method.toUpperCase();
    }

    if (method !== "GET") {
      return originalFetch(input, init);
    }

    let urlKey = "";
    if (typeof input === "string") {
      urlKey = input;
    } else if (input instanceof URL) {
      urlKey = input.toString();
    } else if (input instanceof Request) {
      urlKey = input.url;
    }

    if (urlKey && inFlight.has(urlKey)) {
      const promise = inFlight.get(urlKey);
      if (promise) {
        try {
          const res = await promise;
          return res.clone();
        } catch (err) {
          // If the original request failed, we'll let this one fail too
          throw err;
        }
      }
    }

    const promise = originalFetch(input, init).finally(() => {
      if (urlKey) {
        inFlight.delete(urlKey);
      }
    });

    if (urlKey) {
      inFlight.set(urlKey, promise);
    }

    const res = await promise;
    return res.clone();
  };
}
