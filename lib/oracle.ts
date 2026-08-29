class OracleService {
  private cache: Record<string, Promise<any>> = {};

  preComputeScan(text: string, headers?: Record<string, string>) {
    const key = text.trim();
    if (!key || this.cache[key]) return;

    this.cache[key] = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ text: key })
    }).then(async (res) => {
      if (!res.ok) {
        delete this.cache[key];
        return null;
      }
      return res.json();
    }).catch(() => {
      delete this.cache[key];
      return null;
    });
  }

  async getScanResult(text: string) {
    const key = text.trim();
    if (!key) return null;
    return this.cache[key] || null;
  }
}

export const Oracle = new OracleService();
