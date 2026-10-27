export const inFlight = new Map();
export const cache = new Map();

interface FetchOptions extends RequestInit {
  cacheTtl?: number;
  forceRefresh?: boolean;
}

export async function smartFetch(url: string, options?: FetchOptions) {
  const method = options?.method || 'GET';
  const { cacheTtl = 60000, forceRefresh = false, ...restOptions } = options || {};

  if (method !== 'GET') {
    return fetch(url, restOptions);
  }

  const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null;
  const headers = restOptions.headers ? new Headers(restOptions.headers) : new Headers();
  if (token && (url.startsWith('http://localhost') || url.startsWith('/'))) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const newOptions = { ...restOptions, headers };
  const key = `${url}-${JSON.stringify(Array.from(headers.entries()))}`;

  // Stale-while-revalidate pattern
  if (!forceRefresh && cache.has(key)) {
    const { data, timestamp } = cache.get(key);
    const age = Date.now() - timestamp;

    if (age < cacheTtl) {
      // Return fresh cache
      return new Response(new Blob([JSON.stringify(data)], { type: 'application/json' }), { status: 200, statusText: 'OK' });
    } else {
      // Trigger background refresh but return stale data immediately
      if (!inFlight.has(key)) {
        const promise = fetch(url, newOptions)
          .then(res => res.clone().json().then(data => {
            cache.set(key, { data, timestamp: Date.now() });
            return res;
          }))
          .finally(() => inFlight.delete(key));
        inFlight.set(key, promise);
      }
      return new Response(new Blob([JSON.stringify(data)], { type: 'application/json' }), { status: 200, statusText: 'OK' });
    }
  }

  // Request Coalescing
  if (inFlight.has(key)) return inFlight.get(key).then((res: Response) => res.clone());

  const promise = fetch(url, newOptions).then(res => {
    if (res.ok) {
      // Clone response to read json for cache while returning a valid response
      res.clone().json().then(data => {
        cache.set(key, { data, timestamp: Date.now() });
      }).catch(() => {});
    }
    return res;
  }).finally(() => inFlight.delete(key));

  inFlight.set(key, promise);
  return promise.then((res: Response) => res.clone());
}
