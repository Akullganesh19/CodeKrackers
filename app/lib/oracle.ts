// 🛸 Oracle: Predictive Intelligence Engine
// Anticipates user behavior and manages background prefetching/pre-computation.

interface PredictionCache {
  [key: string]: {
    promise: Promise<any>;
    timestamp: number;
  };
}

const cache: PredictionCache = {};
const TTL = 60000; // 60 seconds

export const Oracle = {
  /**
   * 🛸 Prediction: Route Data Prefetching
   * Predicts that a user is about to navigate to a view that requires specific data.
   */
  prefetchRouteData: (url: string, options: RequestInit = {}) => {
    if (typeof window === 'undefined') return;

    const token = localStorage.getItem('vsdp_token');
    const headers = new Headers(options.headers || {});
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const fetchOptions = { ...options, headers };

    const promise = fetch(url, fetchOptions).catch(() => {
      // Graceful degradation
      return new Response(JSON.stringify({ error: "Oracle prefetch failed" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    cache[url] = { promise, timestamp: Date.now() };
    console.log(`🛸 Oracle: Prefetching ${url} based on predicted navigation`);
  },

  /**
   * Resolves a prediction if it exists.
   */
  resolvePrediction: async (url: string): Promise<Response | null> => {
    const cached = cache[url];
    if (cached !== undefined) {
      if (Date.now() - cached.timestamp < TTL) {
        console.log(`🛸 Oracle: Cache hit for ${url} - eliminating perceived latency`);
        const response = await cached.promise;
        return response.clone();
      } else {
        console.log(`🛸 Oracle: Prediction expired for ${url}`);
        delete cache[url];
      }
    }
    return null;
  },

  /**
   * 🛸 Prediction: Action Pre-computation
   * Predicts the user will click "Analyze" after pausing typing.
   */
  predictSmsScan: (text: string) => {
    if (typeof window === 'undefined' || !text || text.length < 15) return;

    const key = `sms_scan_${text.trim()}`;
    if (cache[key]) return; // Already predicting

    console.log(`🛸 Oracle: User paused typing. Predicting SMS analysis intent...`);

    const token = localStorage.getItem('vsdp_token');

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'dummy_token'}`
      },
      body: JSON.stringify({ text })
    }).then(res => {
      if (!res.ok) throw new Error('Prediction fetch failed');
      return res.json();
    }).catch(err => {
      console.warn('🛸 Oracle: SMS prediction failed or was aborted', err);
      return null;
    });

    cache[key] = { promise, timestamp: Date.now() };
  },

  /**
   * Resolves the SMS scan prediction instantly if it exists
   */
  resolveSmsScan: async (text: string): Promise<any | null> => {
    const key = `sms_scan_${text.trim()}`;
    const cached = cache[key];

    if (cached && (Date.now() - cached.timestamp < TTL)) {
      console.log(`🛸 Oracle: Prediction hit for SMS Scan! Zero latency.`);
      const result = await cached.promise;
      return result;
    }

    console.log(`🛸 Oracle: No valid prediction found for SMS. Falling back to manual.`);
    return null;
  }
};
