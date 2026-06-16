'use client';

import { useEffect } from 'react';

export default function FetchOptimizer() {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if ((window as any).__phantomFetchInstalled) return;
    (window as any).__phantomFetchInstalled = true;

    const originalFetch = window.fetch;
    const inFlight = new Map<string, Promise<Response>>();

    // Store arrayBuffer instead of text to preserve binary data
    const cache = new Map<string, { data: ArrayBuffer, headers: Headers, timestamp: number }>();

    const CACHE_TTL_MS = 5000;

    (window as any).phantomMetrics = {
      coalesced: 0,
      cacheHits: 0,
      network: 0
    };

    // Helper to safely extract headers
    const getHeaders = (init?: RequestInit, req?: Request): Headers => {
      let h = new Headers();
      if (req) {
        req.headers.forEach((v, k) => h.set(k, v));
      }
      if (init?.headers) {
        const initH = new Headers(init.headers);
        initH.forEach((v, k) => h.set(k, v));
      }
      return h;
    };

    window.fetch = async function(input: RequestInfo | URL, init?: RequestInit) {
      const method = init?.method || (input instanceof Request ? input.method : 'GET');

      if (method.toUpperCase() !== 'GET') {
        return originalFetch.apply(this, [input, init]);
      }

      let urlStr = '';
      let reqObj: Request | undefined;

      if (typeof input === 'string') {
        urlStr = input;
      } else if (input instanceof URL) {
        urlStr = input.toString();
      } else if (input instanceof Request) {
        urlStr = input.url;
        reqObj = input;
      }

      const headers = getHeaders(init, reqObj);

      // Respect Cache-Control: no-store / no-cache
      const cacheControl = headers.get('Cache-Control');
      if (cacheControl?.includes('no-store') || cacheControl?.includes('no-cache')) {
        return originalFetch.apply(this, [input, init]);
      }

      const authHeader = headers.get('Authorization') || '';
      const key = `${urlStr}|${authHeader}`;

      // 1. Check Cache
      const cached = cache.get(key);
      if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
        (window as any).phantomMetrics.cacheHits++;
        // Reconstruct response from ArrayBuffer to preserve binary and text alike
        return new Response(cached.data, {
          status: 200,
          headers: cached.headers
        });
      }

      // 2. Request Coalescing
      if (inFlight.has(key)) {
        (window as any).phantomMetrics.coalesced++;
        const res = await inFlight.get(key)!;
        return res.clone();
      }

      // 3. Network Request
      (window as any).phantomMetrics.network++;
      const fetchPromise = originalFetch.apply(this, [input, init])
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            // Process cache async to avoid blocking the stream
            clone.arrayBuffer().then((buffer) => {
              cache.set(key, {
                data: buffer,
                headers: clone.headers,
                timestamp: Date.now()
              });
            }).catch(() => {
              // Ignore cache read errors
            });
          }
          return response;
        })
        .finally(() => {
          inFlight.delete(key);
        });

      inFlight.set(key, fetchPromise);
      const finalRes = await fetchPromise;
      return finalRes.clone();
    };

    return () => {
      window.fetch = originalFetch;
      (window as any).__phantomFetchInstalled = false;
    };
  }, []);

  return null;
}
