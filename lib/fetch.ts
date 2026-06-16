export const inFlight = new Map<string, Promise<Response>>();

declare global {
  interface Window {
    __fetchIntercepted?: boolean;
  }
}

// Global interceptor - if we want to replace window.fetch
export function installGlobalFetchInterceptor() {
  if (typeof window !== 'undefined' && window.fetch && !window.__fetchIntercepted) {
    window.__fetchIntercepted = true;
    const originalFetch = window.fetch;

    window.fetch = async function(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
      const method = init?.method || 'GET';
      if (method.toUpperCase() !== 'GET') {
        return originalFetch(input, init);
      }

      const urlString = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;

      let authHeader = '';
      if (init?.headers) {
        if (init.headers instanceof Headers) {
          authHeader = init.headers.get('Authorization') || '';
        } else if (Array.isArray(init.headers)) {
          const auth = init.headers.find(h => h[0].toLowerCase() === 'authorization');
          if (auth) authHeader = auth[1] as string;
        } else {
          authHeader = ((init.headers as Record<string, string>)['Authorization'] || (init.headers as Record<string, string>)['authorization']) as string || '';
        }
      } else if (input instanceof Request) {
        authHeader = input.headers.get('Authorization') || '';
      }

      const cacheKey = `${urlString}|${authHeader}`;

      if (inFlight.has(cacheKey)) {
        return inFlight.get(cacheKey)!.then(res => res.clone());
      }

      const promise = originalFetch(input, init)
        .finally(() => {
          inFlight.delete(cacheKey);
        });

      inFlight.set(cacheKey, promise);
      return promise.then(res => res.clone());
    };
  }
}
