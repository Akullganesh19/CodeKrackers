// 🔮 Oracle Prediction Engine
// Intercepts window.fetch to provide zero-latency responses for predicted data

let isOracleInitialized = false;
const predictionCache = new Map<string, Promise<Response>>();

// Generate a cache key that includes the URL and authorization header
function generateCacheKey(url: string, method: string, options?: RequestInit): string {
  let authHeader = '';
  if (options && options.headers) {
    if (options.headers instanceof Headers) {
      authHeader = options.headers.get('Authorization') || '';
    } else if (Array.isArray(options.headers)) {
      const auth = options.headers.find(([key]) => key.toLowerCase() === 'authorization');
      if (auth) authHeader = auth[1];
    } else {
      const headersRecord = options.headers as Record<string, string>;
      authHeader = headersRecord['Authorization'] || headersRecord['authorization'] || '';
    }
  }
  return `${method}|${url}|${authHeader}`;
}

export function initializeOracle() {
  if (typeof window === 'undefined' || isOracleInitialized) return;

  const originalFetch = window.fetch;

  window.fetch = async (...args) => {
    const requestArg = args[0];
    const options = args[1];

    let url = '';
    let method = 'GET';

    if (typeof requestArg === 'string' || requestArg instanceof URL) {
        url = requestArg.toString();
        method = options?.method || 'GET';
    } else if (requestArg instanceof Request) {
        url = requestArg.url;
        method = requestArg.method;
    }

    const cacheKey = generateCacheKey(url, method, options);

    // We only use cached predictions for GET requests
    if (method.toUpperCase() === 'GET' && predictionCache.has(cacheKey)) {
      console.log(`🔮 Oracle: Serving zero-latency prediction for ${url}`);
      const cachedPromise = predictionCache.get(cacheKey)!;
      predictionCache.delete(cacheKey); // One-time use per prediction to ensure freshness

      try {
        const cachedResponse = await cachedPromise;
        // Return a cloned response so the body can be read
        return cachedResponse.clone();
      } catch (e) {
        // Fallback to real fetch if prediction failed
        console.log(`🔮 Oracle: Prediction failed, falling back to real fetch.`);
      }
    }

    return originalFetch(...args);
  };

  isOracleInitialized = true;
  console.log("🔮 Oracle: Prediction Engine initialized.");
}

export function predictFetch(url: string, options?: RequestInit) {
  if (typeof window === 'undefined') return;

  const method = options?.method || 'GET';
  const cacheKey = generateCacheKey(url, method, options);

  if (!predictionCache.has(cacheKey)) {
    console.log(`🔮 Oracle: Prefetching predicted data for ${url}`);
    const promise = window.fetch(url, options).then(res => {
        // Read into array buffer to prevent stream lock
        return res.arrayBuffer().then(buffer => {
            return new Response(buffer, {
                status: res.status,
                statusText: res.statusText,
                headers: res.headers
            });
        });
    });
    predictionCache.set(cacheKey, promise);
  }
}
