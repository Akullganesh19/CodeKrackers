'use client';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
if (typeof window !== 'undefined' && !(window as any).__fetchPatched) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).__fetchPatched = true;

  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async function (...args) {
    const [resource, config] = args;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const method = (config as any)?.method?.toUpperCase() || (resource instanceof Request ? resource.method.toUpperCase() : 'GET');

    if (method !== 'GET') {
      return originalFetch.apply(this, args);
    }

    let isRSC = false;
    let hasSignal = false;
    let headersStr = '';
    let url = '';

    if (resource instanceof Request) {
      url = resource.url;
      hasSignal = !!resource.signal;
      isRSC = resource.headers.has('RSC') || resource.headers.has('rsc');
      const h: Record<string, string> = {};
      resource.headers.forEach((val, key) => { h[key] = val; });
      headersStr = JSON.stringify(h);
    } else {
      url = resource.toString();
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cfg = config as any;
    if (cfg) {
      if (cfg.signal) hasSignal = true;
      if (cfg.headers) {
        if (cfg.headers instanceof Headers) {
          isRSC = isRSC || cfg.headers.has('RSC') || cfg.headers.has('rsc');
          const h: Record<string, string> = {};
          cfg.headers.forEach((val: string, key: string) => { h[key] = val; });
          headersStr += JSON.stringify(h);
        } else if (Array.isArray(cfg.headers)) {
          headersStr += JSON.stringify(cfg.headers);
        } else {
          isRSC = isRSC || !!cfg.headers['RSC'] || !!cfg.headers['rsc'];
          headersStr += JSON.stringify(cfg.headers);
        }
      }
    }

    if (isRSC || hasSignal) {
      return originalFetch.apply(this, args);
    }

    const cacheKey = `${url}|${headersStr}`;

    if (inFlight.has(cacheKey)) {
      console.log(`[Phantom] Coalesced duplicate fetch for: ${url}`);
      return inFlight.get(cacheKey)!.then(res => res.clone());
    }

    const promise = originalFetch.apply(this, args);
    const sharedPromise = promise.finally(() => {
      inFlight.delete(cacheKey);
    });

    inFlight.set(cacheKey, sharedPromise);
    return sharedPromise.then(res => res.clone());
  };
}

export default function PhantomInfrastructure() {
  return null;
}
