export const phantomCache: Record<string, { promise: Promise<Response>, timestamp: number }> = {};
export const inFlightCache: Record<string, Promise<Response>> = {};
export const cacheKeys: string[] = [];

const CACHE_TTL_MS = 10000; // 10 seconds TTL

export async function phantomFetch(url: string, options?: RequestInit): Promise<Response> {
  const method = options?.method?.toUpperCase() || 'GET';

  if (method !== 'GET') {
    return fetch(url, options);
  }

  let headersString = '';
  if (options?.headers) {
    if (options.headers instanceof Headers) {
      headersString = JSON.stringify(Object.fromEntries(options.headers.entries()));
    } else {
      headersString = JSON.stringify(options.headers);
    }
  }

  const cacheKey = `${url}|${headersString}`;

  if (inFlightCache[cacheKey] !== undefined) {
    const res = await inFlightCache[cacheKey];
    return res.clone();
  }

  const now = Date.now();
  if (phantomCache[cacheKey] !== undefined) {
    const cachedEntry = phantomCache[cacheKey];
    if (now - cachedEntry.timestamp < CACHE_TTL_MS) {
      try {
        const cachedRes = await cachedEntry.promise;
        return cachedRes.clone();
      } catch (e) {
        delete phantomCache[cacheKey];
      }
    } else {
      delete phantomCache[cacheKey]; // Evict stale
    }
  }

  const p = fetch(url, options)
    .then(res => {
      if (!res.ok) {
         delete phantomCache[cacheKey];
      }
      return res;
    })
    .catch(err => {
      delete phantomCache[cacheKey];
      throw err;
    })
    .finally(() => {
      delete inFlightCache[cacheKey];
    });

  inFlightCache[cacheKey] = p;
  phantomCache[cacheKey] = { promise: p, timestamp: now };

  const existingIdx = cacheKeys.indexOf(cacheKey);
  if (existingIdx !== -1) {
    cacheKeys.splice(existingIdx, 1);
  }
  cacheKeys.push(cacheKey);

  if (cacheKeys.length > 50) {
    const oldestKey = cacheKeys.shift();
    if (oldestKey) delete phantomCache[oldestKey];
  }

  const res = await p;
  return res.clone();
}
