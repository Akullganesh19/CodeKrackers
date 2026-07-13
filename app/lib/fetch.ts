// Phantom Fetch - Invisible Infrastructure for caching, request coalescing, and retries.
export interface PhantomOptions extends RequestInit {
  ttl?: number;
  retries?: number;
}

const inFlight: Record<string, Promise<Response>> = {};
const cache: Record<string, { response: Response; expiresAt: number }> = {};

export async function phantomFetch(input: RequestInfo | URL, options: PhantomOptions = {}): Promise<Response> {
  const { ttl = 5000, retries = 3, ...fetchOptions } = options;
  const isGet = !fetchOptions.method || fetchOptions.method.toUpperCase() === 'GET';

  // Extract URL string correctly
  let urlStr = '';
  if (typeof input === 'string') {
    urlStr = input;
  } else if (input instanceof URL) {
    urlStr = input.toString();
  } else if (input && typeof input === 'object' && 'url' in input) {
    urlStr = input.url;
  }

  // Cache key includes url and stringified headers if they exist
  let headersKey = '';
  if (fetchOptions.headers) {
    if (fetchOptions.headers instanceof Headers) {
      headersKey = JSON.stringify(Object.fromEntries(fetchOptions.headers.entries()));
    } else {
      headersKey = JSON.stringify(fetchOptions.headers);
    }
  }
  const key = `${urlStr}-${isGet ? 'GET' : fetchOptions.method || 'GET'}-${headersKey}`;

  // 1. Check valid cache
  if (isGet && key in cache) {
    const entry = cache[key];
    if (Date.now() < entry.expiresAt) {
      // Return cloned response so body can be read multiple times
      return entry.response.clone();
    } else {
      delete cache[key];
    }
  }

  // 2. Request Coalescing (In-flight deduping)
  if (isGet && key in inFlight) {
    const promise = inFlight[key];
    try {
      const res = await promise;
      return res.clone();
    } catch (e) {
      // If the in-flight promise fails, we fall through and retry our own execution
    }
  }

  // 3. Execution with Retries
  const execute = async (attempt: number): Promise<Response> => {
    try {
      // Execute the native fetch
      const res = await fetch(input, fetchOptions);
      // We explicitly DO NOT throw on !res.ok here to maintain exact native fetch contract.
      // fetch only rejects on network failures (e.g., DNS error, disconnected).
      return res;
    } catch (error) {
      // Only retry GET requests on actual network failures to avoid duplicate POST side-effects
      if (isGet && attempt < retries) {
        // Exponential backoff
        await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 100));
        return execute(attempt + 1);
      }
      throw error;
    }
  };

  const fetchPromise = execute(1).then(res => {
    // Only cache successful GET requests
    if (isGet && res.ok) {
      cache[key] = {
        response: res.clone(),
        expiresAt: Date.now() + ttl,
      };
    }
    return res;
  }).catch(error => {
    if (isGet) {
      delete cache[key]; // Do not cache failures
    }
    throw error;
  }).finally(() => {
    if (isGet) {
      delete inFlight[key];
    }
  });

  if (isGet) {
    inFlight[key] = fetchPromise;
  }

  const res = await fetchPromise;
  return res.clone();
}
