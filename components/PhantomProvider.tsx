'use client'

import React from 'react'

// Map to store in-flight requests for request coalescing
const inFlight = new Map<string, Promise<Response>>();

declare global {
  interface Window {
    __fetchPatched?: boolean;
  }
}

// We patch window.fetch globally outside the React lifecycle
// so it is applied immediately upon script execution.
if (typeof window !== 'undefined' && !window.__fetchPatched) {
  window.__fetchPatched = true;
  const originalFetch = window.fetch;

  window.fetch = async function (...args) {
    const url = typeof args[0] === 'string' ? args[0] : (args[0] instanceof URL ? args[0].toString() : (args[0] instanceof Request ? args[0].url : ''));
    const options = args[1] || {};

    const requestObj = args[0] instanceof Request ? args[0] : null;
    const method = (options.method || (requestObj ? requestObj.method : 'GET')).toUpperCase();
    const signal = options.signal || (requestObj ? requestObj.signal : null);

    // Extract headers to check for Next.js internal RSC requests and to build a safe cache key
    let headersObj: Record<string, string> = {};
    const rawHeaders = options.headers || (requestObj ? requestObj.headers : null);
    if (rawHeaders) {
      if (rawHeaders instanceof Headers) {
        rawHeaders.forEach((value, key) => { headersObj[key.toLowerCase()] = value; });
      } else if (Array.isArray(rawHeaders)) {
        rawHeaders.forEach(([key, value]) => { headersObj[key.toLowerCase()] = value; });
      } else {
        Object.entries(rawHeaders).forEach(([key, value]) => {
          headersObj[key.toLowerCase()] = String(value);
        });
      }
    }

    // Do not coalesce non-GET requests, requests with an AbortSignal, or Next.js RSC requests
    if (method === 'GET' && url && !signal && !headersObj['rsc']) {
      // Create a cache key combining URL and serialized headers to prevent conflation
      const cacheKey = `${url}|${JSON.stringify(headersObj)}`;

      if (inFlight.has(cacheKey)) {
        // Return a cloned response for duplicate requests so that consumers
        // don't try to consume the same body stream and throw 'body already consumed'.
        return inFlight.get(cacheKey)!.then(res => res.clone());
      }

      const promise = originalFetch.apply(window, args)
        .finally(() => {
          inFlight.delete(cacheKey);
        });

      inFlight.set(cacheKey, promise);

      // We must return a clone for ALL callers, including the first one.
      // If we return the raw response to the first caller, it might consume the body stream,
      // making it impossible for subsequent duplicate callers to call .clone() when the promise resolves.
      return promise.then(res => res.clone());
    }

    // For non-GET requests or unparseable URLs, pass through transparently
    return originalFetch.apply(window, args);
  };
}

export function PhantomProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
