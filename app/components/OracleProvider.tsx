'use client'

import React from 'react';

let isInitialized = false;
let originalFetch: typeof fetch;

const predictionCache = new Map<string, Promise<Response>>();
const debounceTimers = new Map<string, NodeJS.Timeout>();

export function predictAction(url: string, options: RequestInit) {
  if (typeof window === 'undefined') return;

  const method = options.method || 'GET';
  const bodyStr = options.body ? String(options.body) : '';
  const cacheKey = `${method}:${url}:${bodyStr}`;
  const timerId = `${method}:${url}`; // static identifier for the endpoint

  if (debounceTimers.has(timerId)) {
    clearTimeout(debounceTimers.get(timerId)!);
  }

  const timer = setTimeout(() => {
    debounceTimers.delete(timerId);

    try {
      const fetchPromise = originalFetch(url, options).then(async (res) => {
        // Store body as ArrayBuffer to support binary payloads
        const buffer = await res.clone().arrayBuffer();
        return new Response(buffer, {
          status: res.status,
          statusText: res.statusText,
          headers: res.headers,
        });
      });
      predictionCache.set(cacheKey, fetchPromise);
    } catch (e) {
      console.error('Predictive fetch failed', e);
    }
  }, 500);

  debounceTimers.set(timerId, timer);
}

export function OracleProvider({ children }: { children: React.ReactNode }) {
  if (typeof window !== 'undefined' && !isInitialized) {
    isInitialized = true;
    originalFetch = window.fetch;

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = init?.method || 'GET';
      const bodyStr = init?.body ? String(init.body) : '';
      const cacheKey = `${method}:${url}:${bodyStr}`;

      if (predictionCache.has(cacheKey)) {
        const cachedPromise = predictionCache.get(cacheKey)!;
        // Remove promise from cache immediately to prevent body stream from being read twice
        predictionCache.delete(cacheKey);

        try {
          const res = await cachedPromise;
          return res.clone();
        } catch (e) {
          return originalFetch(input, init);
        }
      }

      return originalFetch(input, init);
    };
  }

  return <>{children}</>;
}
