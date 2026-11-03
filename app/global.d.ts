export {}; declare global { interface Window { _prefetchCache: Record<string, Promise<Response>>; } }
