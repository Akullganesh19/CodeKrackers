class Oracle {
  private cache: Record<string, Promise<any> | undefined> = {};

  preComputeScan(text: string, headers?: Record<string, string>) {
    if (!text || text.length < 10) return; // Wait for meaningful input

    const key = text.trim();
    if (this.cache[key] !== undefined) return; // Already computing or computed

    this.cache[key] = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {}),
      },
      body: JSON.stringify({ text }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Predictive fetch failed');
        }
        return res.json();
      })
      .catch((err) => {
        console.warn('Oracle prediction failed, gracefully degrading', err);
        delete this.cache[key];
        return null;
      });
  }

  async getScanResult(text: string): Promise<any | null> {
    const key = text.trim();
    if (this.cache[key] !== undefined) {
      const result = await this.cache[key];
      // Clean up after consuming
      delete this.cache[key];
      return result;
    }
    return null;
  }
}

export const oracle = new Oracle();
