export const Oracle = (() => {
  const cache: Record<string, Promise<Response>> = {};

  const preComputeScan = (text: string, token: string | null) => {
    if (!text.trim()) return;

    // Use a unique key based on the text to avoid redundant pre-computation
    const key = text.trim();
    if (key in cache) return;

    console.log(`[Oracle] Pre-computing scan for: ${key.substring(0, 20)}...`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    }).then(res => {
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      return res;
    }).catch(err => {
      console.error(`[Oracle] Pre-computation failed:`, err);
      // Delete the cache entry so that manual retry will issue a new request
      delete cache[key];
      // Return a graceful fallback response to prevent Unhandled Promise Rejection
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    cache[key] = promise;
  };

  const getScanResult = (text: string): Promise<Response> | undefined => {
    const key = text.trim();
    if (key in cache) {
      console.log(`[Oracle] Serving pre-computed result for: ${key.substring(0, 20)}...`);
      const promise = cache[key];
      // Delete from cache so it's only used once, ensuring fresh fetches later if needed
      delete cache[key];
      // Clone the response so the body can be read multiple times if needed elsewhere
      return promise.then(res => res.clone());
    }
    return undefined;
  };

  return {
    preComputeScan,
    getScanResult
  };
})();
