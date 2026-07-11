// Predictive Intelligence Engine (Oracle)
export class OracleEngine {
  private scanCache: Record<string, Promise<Response>> = {};

  // Anticipates user will analyze the pasted text.
  // We trigger the scan before they even click "Analyze".
  preComputeScan(text: string, token: string) {
    if (!text || text.length < 5) return;

    const key = `scan_${text}`;
    if (key in this.scanCache) return; // Already computing or computed

    console.log(`[Oracle 🛸] Pre-computing scan for: "${text.substring(0, 15)}..."`);

    const promise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res;
    }).catch(err => {
      console.error(`[Oracle 🛸] Pre-computation failed:`, err);
      // Clean up failed entry so manual retry will attempt fresh network request
      delete this.scanCache[key];
      // Graceful fallback to avoid unhandled rejections poisoning the app state
      return new Response(JSON.stringify({ error: "Prediction failed" }), { status: 500 });
    });

    this.scanCache[key] = promise;
  }

  // Resolves the pre-computed response if it exists, cloning it to prevent 'body stream already read' errors.
  async resolvePrediction(text: string): Promise<Response | null> {
    const key = `scan_${text}`;
    const cachedPromise = this.scanCache[key];

    if (cachedPromise) {
      console.log(`[Oracle 🛸] Resolving pre-computed prediction! (zero perceived latency)`);
      const res = await cachedPromise;
      if (!res.ok) {
         delete this.scanCache[key];
         return null;
      }
      return res.clone(); // MUST clone so body can be consumed by caller
    }

    return null;
  }
}

export const Oracle = new OracleEngine();
