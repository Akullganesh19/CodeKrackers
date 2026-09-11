'use client';

// Apply the patch outside the React lifecycle
if (typeof window !== 'undefined' && !(window as any).__fetchPatched) {
  (window as any).__fetchPatched = true;

  const originalFetch = window.fetch;
  const inFlightRequests = new Map<string, Promise<Response>>();

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const method = init?.method?.toUpperCase() || 'GET';

    let isRSC = false;
    if (init?.headers) {
      if (init.headers instanceof Headers) {
        isRSC = init.headers.has('RSC') || init.headers.has('rsc');
      } else if (Array.isArray(init.headers)) {
        isRSC = init.headers.some(([k]) => k.toLowerCase() === 'rsc');
      } else {
        const h = init.headers as Record<string, string>;
        isRSC = !!h['RSC'] || !!h['rsc'];
      }
    }

    const hasSignal = !!init?.signal;

    // Bypass coalescing for non-GET, Next.js internal RSC requests, and requests with AbortSignal
    if (method !== 'GET' || isRSC || hasSignal) {
      return originalFetch(input, init);
    }

    let urlStr = '';
    if (typeof input === 'string') {
      urlStr = input;
    } else if (input instanceof URL) {
      urlStr = input.toString();
    } else if (typeof input === 'object' && input !== null && 'url' in input) {
      urlStr = (input as any).url;
    }

    let headersStr = '';
    try {
      if (init?.headers) {
        if (init.headers instanceof Headers) {
          const h: Record<string, string> = {};
          init.headers.forEach((v, k) => { h[k] = v; });
          headersStr = JSON.stringify(h);
        } else {
          headersStr = JSON.stringify(init.headers);
        }
      }
    } catch (e) {
      // Fallback if stringify fails
    }

    const cacheKey = `${urlStr}|${headersStr}`;

    if (inFlightRequests.has(cacheKey)) {
      const promise = inFlightRequests.get(cacheKey) as Promise<Response>;
      const res = await promise;
      return res.clone();
    }

    const promise = originalFetch(input, init).finally(() => {
      inFlightRequests.delete(cacheKey);
    });

    inFlightRequests.set(cacheKey, promise);

    const res = await promise;
    return res.clone();
  };
}

export default function PhantomFetch() {
  return null;
}
