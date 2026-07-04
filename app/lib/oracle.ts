// 🛸 Oracle Predictive Engine
// Anticipates user behavior to make the application feel impossibly fast.
// Predicts next actions based on current signals (mouse movement, typing cadence).

type CacheStore = Record<string, Promise<any>>;
const predictionCache: CacheStore = {};

export const Oracle = {
  /**
   * 1. BEHAVIORAL PRE-COMPUTATION
   * Signal used: User typing cadence (debounced text input)
   * Prediction: The user will eventually click "Analyze SMS".
   * Action: Run the ML inference in the background BEFORE they click.
   */
  preComputeScan: (text: string) => {
    if (text.length < 20) return; // Too short to predict

    const hash = text.trim();
    if (predictionCache[hash] !== undefined) return; // Already computing or cached

    console.log("🛸 Oracle: Predictive pre-computation triggered for SMS scan");
    const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') || 'dummy_token' : 'dummy_token';

    // Store the raw promise in our cache.
    predictionCache[hash] = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: text.trim() })
    })
    .then(res => {
      if (!res.ok) {
        delete predictionCache[hash];
        throw new Error("Oracle prediction failed gracefully.");
      }
      return res;
    })
    .catch((err) => {
      // Degrade gracefully - silently discard failed predictions
      delete predictionCache[hash];
      return null;
    });
  },

  /**
   * 2. ROUTE DATA PREFETCHING
   * Signal used: Hovering over a navigation link
   * Prediction: The user will click the link and navigate to the page.
   * Action: Prefetch the API data required by that page so it loads instantly.
   */
  prefetchRouteData: (route: string) => {
    if (typeof window === 'undefined') return;

    const token = localStorage.getItem('vsdp_token') || 'dummy_token';
    const fetchApi = (url: string) => {
      if (predictionCache[url] === undefined) {
        console.log(`🛸 Oracle: Prefetching API data for anticipated route: ${route} -> ${url}`);
        predictionCache[url] = fetch(`http://localhost:8000${url}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => {
          if (!res.ok) {
            delete predictionCache[url];
            throw new Error("Oracle prefetch failed");
          }
          return res;
        })
        .catch(() => null); // Fail silently
      }
    };

    // Mapped predictions: If user goes to X, they need Y data.
    if (route === '/dashboard') {
      fetchApi('/api/analytics/dashboard-summary');
    } else if (route === '/analytics') {
      fetchApi('/api/analytics/dashboard-summary');
      fetchApi('/api/analytics/threat_map');
    } else if (route === '/sms-scanner') {
      // Example prefetch for safety score if that's a thing
    }
  },

  /**
   * Retrieves a cached Response or performs a real fetch if prediction was missed.
   */
  resolvePrediction: async (cacheKey: string, fallbackFetch: () => Promise<Response>): Promise<Response> => {
    if (predictionCache[cacheKey] !== undefined) {
      console.log(`🛸 Oracle: Cache hit for ${cacheKey}! Serving predicted result.`);
      const cachedRes = await predictionCache[cacheKey];
      if (cachedRes) {
        // Memory directive: Always clone the response so it can be consumed multiple times safely
        return cachedRes.clone();
      }
    }

    // Prediction missed or not fired yet
    return fallbackFetch();
  }
};
