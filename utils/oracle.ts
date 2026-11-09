// Oracle Engine: Predictive Request Coalescing and Prefetching

// Store in-flight requests to prevent duplicate network calls
const inFlight = new Map<string, Promise<Response>>();
// Short-lived cache for GET requests
const cache = new Map<string, { data: Response, timestamp: number }>();
const CACHE_TTL = 15000; // 15 seconds

let isPatched = false;

export function initOracleEngine() {
  if (typeof window === 'undefined' || isPatched) return;
  isPatched = true;

  const originalFetch = window.fetch;

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    let url = '';
    let method = 'GET';

    if (input instanceof Request) {
      url = input.url;
      method = input.method;
    } else if (typeof input === 'string') {
      url = input;
      method = init?.method || 'GET';
    } else {
      url = input.toString();
      method = init?.method || 'GET';
    }

    if (method !== 'GET') {
      return originalFetch(input, init);
    }

    const cacheKey = url;

    // 1. Check cache
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data.clone();
    }

    // 2. Check in-flight
    if (inFlight.has(cacheKey)) {
      const res = await inFlight.get(cacheKey)!;
      return res.clone();
    }

    // 3. Make request
    const promise = originalFetch(input, init).then(res => {
      if (res.ok) {
        cache.set(cacheKey, { data: res.clone(), timestamp: Date.now() });
      }
      inFlight.delete(cacheKey);
      return res;
    }).catch(err => {
      inFlight.delete(cacheKey);
      throw err;
    });

    inFlight.set(cacheKey, promise);
    const result = await promise;
    return result.clone();
  };
}

// Maps UI routes to their primary API dependencies
const ROUTE_PREDICTIONS: Record<string, string[]> = {
  '/dashboard': ['http://localhost:8000/api/analytics/dashboard-summary'],
  '/analytics': ['http://localhost:8000/api/analytics/dashboard-summary', 'http://localhost:8000/api/analytics/threat_map'],
};

export function predictAndPrefetch(route: string, tokenOverride?: string) {
  if (typeof window === 'undefined') return;
  const endpoints = ROUTE_PREDICTIONS[route];
  if (!endpoints) return;

  const token = tokenOverride || localStorage.getItem('vsdp_token');
  if (!token) return;

  endpoints.forEach(url => {
    // We use window.fetch here so it gets caught by our interceptor
    // which handles deduplication and caching.
    window.fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    }).catch(() => { /* silent fail */ });
  });
}
