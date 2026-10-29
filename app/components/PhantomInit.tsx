'use client';
import { useEffect } from 'react';

export default function PhantomInit() {
  useEffect(() => {
    if (typeof window === 'undefined' || (window as any)._phantomInitialized) return;
    (window as any)._phantomInitialized = true;

    const originalFetch = window.fetch;
    const inFlight = new Map<string, Promise<Response>>();

    window.fetch = async (...args) => {
      const [resource, config] = args;

      let method = 'GET';
      let hasSignal = false;
      let url = '';
      let headersStr = '';
      let isNoStore = false;

      if (resource instanceof Request) {
        method = resource.method || 'GET';
        hasSignal = !!resource.signal;
        url = resource.url;
        // Basic header serialization for Request object (imperfect but better than {})
        const headerObj: Record<string, string> = {};
        resource.headers.forEach((value, key) => {
           headerObj[key] = value;
        });
        headersStr = JSON.stringify(headerObj);
        isNoStore = resource.cache === 'no-store';
      } else {
        url = String(resource);
      }

      if (config) {
        if (config.method) method = config.method;
        if (config.signal) hasSignal = true;
        if (config.cache === 'no-store') isNoStore = true;

        if (config.headers) {
          if (config.headers instanceof Headers) {
            const headerObj: Record<string, string> = {};
            config.headers.forEach((value, key) => {
               headerObj[key] = value;
            });
            headersStr = JSON.stringify(headerObj);
          } else {
             headersStr = JSON.stringify(config.headers);
          }
        }
      }

      if (method.toUpperCase() !== 'GET' || hasSignal || isNoStore) {
        return originalFetch(...args);
      }

      const cacheKey = `${url}|${headersStr}`;

      if (inFlight.has(cacheKey)) {
        if (!(window as any)._phantomSavedRequests) (window as any)._phantomSavedRequests = 0;
        (window as any)._phantomSavedRequests++;
        console.log(`🌀 Phantom: Coalesced duplicate request to ${url}`);

        const response = await inFlight.get(cacheKey)!;
        return response.clone();
      }

      const promise = originalFetch(...args).finally(() => {
        inFlight.delete(cacheKey);
      });

      inFlight.set(cacheKey, promise);
      const response = await promise;
      return response.clone();
    };
  }, []);

  return null;
}
