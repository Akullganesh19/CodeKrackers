// lib/oracle.ts
const predictionCache: Record<string, Promise<unknown>> = {};
let debounceTimer: NodeJS.Timeout | null = null;

export const preComputeScan = (
  text: string,
  urlOverride?: string,
  headers?: Record<string, string>,
  body?: Record<string, unknown>,
  keyOverride?: string
) => {
  if (!text.trim() || text.length < 5) return;

  const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') || 'dummy_token' : 'dummy_token';
  const url = urlOverride || 'http://localhost:8000/api/analytics/scan';
  const key = keyOverride || `${url}-${text}`;

  // Debounce the fetch to avoid spamming the backend on every keystroke
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }

  debounceTimer = setTimeout(() => {
    if (!(key in predictionCache)) {
      const promise = fetch(url, {
        method: 'POST',
        headers: headers || {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: body ? JSON.stringify(body) : JSON.stringify({ text })
      }).catch(_e => {
        // background error cleanup
        delete predictionCache[key];
        throw _e;
      });
      predictionCache[key] = promise;
    }
  }, 500); // 500ms debounce
};

export const getScanResult = (text: string, urlOverride?: string, keyOverride?: string) => {
  const url = urlOverride || 'http://localhost:8000/api/analytics/scan';
  const key = keyOverride || `${url}-${text}`;

  if (key in predictionCache) {
    const promise = predictionCache[key];
    delete predictionCache[key]; // Can only read stream once
    return promise;
  }
  return null;
};
