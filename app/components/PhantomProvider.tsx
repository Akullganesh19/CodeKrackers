"use client";

import { useEffect } from "react";

// Initialize outside the React lifecycle so the patch applies
// immediately upon script evaluation, intercepting initial page-load requests.
if (typeof window !== "undefined" && !(window as any).__phantom_initialized) {
  (window as any).__phantom_initialized = true;

  const nativeFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async function (
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> {
    // Safely extract URL
    const url =
      typeof input === "string"
        ? input
        : input instanceof URL
        ? input.toString()
        : input.url;

    // Safely extract Method
    const method = (
      init?.method ||
      (input instanceof Request ? input.method : "GET")
    ).toUpperCase();

    // Safely extract headers
    let headers = new Headers();
    try {
      headers = new Headers(
        init?.headers || (input instanceof Request ? input.headers : undefined)
      );
    } catch (e) {
      // ignore
    }

    // Bypass caching conditions
    const isGet = method === "GET";
    const isNoStore = init?.cache === "no-store";
    const isRSC = headers.has("RSC") || headers.has("Next-Router-Prefetch");

    if (!isGet || isNoStore || isRSC) {
      return nativeFetch(input, init);
    }

    // Include Authorization in cache key to avoid deduplicating mixed auth states
    const authHeader = headers.get("Authorization") || "";
    const cacheKey = `${url}|${authHeader}`;

    if (inFlight.has(cacheKey)) {
      return inFlight.get(cacheKey)!.then((res) => res.clone());
    }

    const promise = nativeFetch(input, init);
    inFlight.set(cacheKey, promise);

    promise.finally(() => {
      inFlight.delete(cacheKey);
    }).catch(() => {
      // Catch the derived promise branch to prevent Unhandled Promise Rejections
      // if the underlying nativeFetch rejects (e.g. DNS failure)
    });

    return promise.then((res) => res.clone());
  };
}

export function PhantomProvider({ children }: { children: React.ReactNode }) {
  // Empty effect, logic handled at module scope
  useEffect(() => {}, []);
  return <>{children}</>;
}
