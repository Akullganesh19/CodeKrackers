const inFlight = new Map<string, Promise<Response>>();
const cache: Record<string, { promise: Promise<Response>, timestamp: number }> = {};
const TTL_MS = 60000; // 1 minute

export async function phantomFetch(url: string | URL, options?: RequestInit): Promise<Response> {
  const urlStr = url.toString();

  let headersKey = "";
  if (options?.headers) {
    if (options.headers instanceof Headers) {
      headersKey = JSON.stringify(Object.fromEntries(options.headers.entries()));
    } else {
      headersKey = JSON.stringify(options.headers);
    }
  }

  const cacheKey = `${urlStr}|${options?.method || 'GET'}|${headersKey}`;
  const isCacheable = !options?.method || options.method.toUpperCase() === 'GET';

  if (!isCacheable) {
    return fetch(url, options);
  }

  if (cache[cacheKey] !== undefined) {
    const entry = cache[cacheKey];
    const age = Date.now() - entry.timestamp;

    if (age < TTL_MS) {
      if (age > TTL_MS / 2) {
        // Stale-while-revalidate background refresh
        fetch(url, options)
          .then(res => {
            if (!res.ok) {
              delete cache[cacheKey];
            } else {
              cache[cacheKey] = { promise: Promise.resolve(res.clone()), timestamp: Date.now() };
            }
          })
          .catch(() => { /* silent */ });
      }

      const cachedRes = await entry.promise;
      return cachedRes.clone();
    } else {
      delete cache[cacheKey];
    }
  }

  if (inFlight.has(cacheKey)) {
    const sharedRes = await inFlight.get(cacheKey)!;
    return sharedRes.clone();
  }

  const fetchPromise = fetch(url, options).then(res => {
    if (!res.ok) {
      delete cache[cacheKey];
    } else {
      cache[cacheKey] = { promise: Promise.resolve(res.clone()), timestamp: Date.now() };
    }
    return res;
  }).catch(err => {
    delete cache[cacheKey];
    throw err;
  });

  inFlight.set(cacheKey, fetchPromise);
  fetchPromise.finally(() => inFlight.delete(cacheKey));

  const res = await fetchPromise;
  return res.clone();
}
