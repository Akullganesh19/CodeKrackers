const cache: Record<string, Promise<Response>> = {};

export const Oracle = {
  preComputeScan(text: string, token: string) {
    const key = text.trim();
    if (!key || key in cache) return;

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.clone(); // clone it because Response bodies can only be read once, and what if we want it? No, if we clone, it's safe. But wait, getScanResult returns a Promise<Response>.
    }).catch(err => {
      delete cache[key];
      // Return a graceful fallback response if possible, or throw.
      // The prompt says: "delete the cache entry on failure, and return a graceful fallback response"
      return new Response(JSON.stringify({
        isScam: false,
        confidence: 0,
        riskFactors: [],
        recommendation: "Error connecting to backend.",
        tags: ["error"]
      }), { status: 200, statusText: "Fallback", headers: { 'Content-Type': 'application/json' } });
    });

    cache[key] = promise;
  },

  getScanResult(text: string, token: string): Promise<Response> {
    const key = text.trim();
    if (key in cache) {
      const promise = cache[key];
      delete cache[key];
      // Return a clone if we need to? Or just the promise which resolves to the cloned response above.
      // Above we did res.clone(), so returning the promise will give us the cloned response.
      // But wait, the fallback response is NOT cloned. Actually we can just resolve to a Response and the consumer will read it.
      return promise;
    }

    return fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    });
  }
};
