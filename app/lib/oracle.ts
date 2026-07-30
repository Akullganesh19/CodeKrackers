const predictiveCache: Record<string, Promise<Response | null>> = {};

export const preComputeScan = (text: string, token: string) => {
  if (!text.trim()) return;
  const hash = text.trim();

  if (hash in predictiveCache) return;

  const keys = Object.keys(predictiveCache);
  if (keys.length >= 10) {
    delete predictiveCache[keys[0]];
  }

  predictiveCache[hash] = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text })
  }).catch((error) => {
    console.error("Predictive fetch failed (silenced):", error);
    return null;
  });
};

export const getScanResult = async (text: string): Promise<Response | null> => {
  const hash = text.trim();

  if (hash in predictiveCache) {
    console.log("🛸 Oracle: Cache hit for scan prediction!");
    const responsePromise = predictiveCache[hash];
    delete predictiveCache[hash];

    const response = await responsePromise;
    if (response) {
      return response.clone();
    }
  }

  return null;
};
