'use client';

import { useEffect } from 'react';

export default function RequestCoalescer() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    if ((window as any).__fetchPatched) return;
    (window as any).__fetchPatched = true;

    const originalFetch = window.fetch;
    const inFlight = new Map();

    window.fetch = async (...args) => {
      let url = '';
      let method = 'GET';
      let signal = undefined;

      const input = args[0];
      const init = args[1];

      if (input instanceof Request) {
        url = input.url;
        method = input.method || 'GET';
        signal = input.signal;
      } else {
        url = input.toString();
        if (init) {
          method = init.method || 'GET';
          signal = init.signal;
        }
      }

      if (method.toUpperCase() !== 'GET') {
        return originalFetch(...args);
      }

      const cacheKey = url;

      if (inFlight.has(cacheKey)) {
        const res = await inFlight.get(cacheKey);
        return res.clone();
      }

      const promise = originalFetch(...args).then(res => {
        inFlight.delete(cacheKey);
        return res;
      }).catch(err => {
        inFlight.delete(cacheKey);
        throw err;
      });

      inFlight.set(cacheKey, promise);

      const res = await promise;
      return res.clone();
    };
  }, []);

  return null;
}
