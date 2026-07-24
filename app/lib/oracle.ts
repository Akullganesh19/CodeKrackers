'use client'

const MAX_CACHE_SIZE = 10;
const predictiveCache: Record<string, Promise<Response | null>> = {};

export const preComputeScan = (text: string, token: string) => {
  if (!text || text.length < 10) return;

  const key = text.trim();
  if (key in predictiveCache) return;

  const keys = Object.keys(predictiveCache);
  if (keys.length >= MAX_CACHE_SIZE) {
    delete predictiveCache[keys[0]];
  }

  const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text })
  }).catch((error) => {
    console.error("Predictive scan error:", error);
    return null;
  });

  predictiveCache[key] = fetchPromise;
};

export const getScanResult = async (text: string): Promise<Response | null> => {
  const key = text.trim();
  if (key in predictiveCache) {
    const responsePromise = predictiveCache[key];
    delete predictiveCache[key];

    const response = await responsePromise;
    if (response) {
      return response.clone();
    }
  }
  return null;
};
