// Request Coalescing Cache
const inFlight = new Map<string, Promise<Response>>();

export async function dedupedFetch(url: string, options?: RequestInit): Promise<Response> {
  const method = options?.method?.toUpperCase() || 'GET';

  // We only coalesce GET requests
  if (method !== 'GET') {
    return fetch(url, options);
  }

  // Create a cache key using URL and specific headers (like Auth)
  const authHeader = options?.headers ? (options.headers as Record<string, string>)['Authorization'] : '';
  const cacheKey = `${url}|${authHeader}`;

  if (inFlight.has(cacheKey)) {
    // Return a clone of the response from the coalesced promise
    // because the response body can only be consumed once
    return inFlight.get(cacheKey)!.then(res => res.clone());
  }

  const promise = fetch(url, options).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);

  return promise.then(res => res.clone());
}
