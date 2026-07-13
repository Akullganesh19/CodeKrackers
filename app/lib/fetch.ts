const cache: Record<string, { promise: Promise<Response>, time: number }> = {};
const TTL = 10000; // 10 seconds

export const phantomFetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    let urlStr = '';
    if (typeof input === 'string') {
        urlStr = input;
    } else if (input instanceof URL) {
        urlStr = input.toString();
    } else if (input && typeof input === 'object' && 'url' in input) {
        urlStr = input.url;
    }

    const headersObj = init?.headers instanceof Headers
        ? Object.fromEntries(init.headers.entries())
        : init?.headers || {};

    const cacheKey = JSON.stringify({
        url: urlStr,
        method: init?.method || 'GET',
        headers: headersObj,
        body: init?.body
    });

    const now = Date.now();
    if (cacheKey in cache) {
        const cached = cache[cacheKey];
        if (now - cached.time < TTL) {
            console.log(`[Phantom 🌀] Coalescing fetch for ${urlStr}`);
            const res = await cached.promise;
            return res.clone();
        } else {
            delete cache[cacheKey];
        }
    }

    const fetchPromise = fetch(input, init).then(res => {
        if (!res.ok) {
            delete cache[cacheKey];
            return res;
        }
        return res;
    }).catch(err => {
        delete cache[cacheKey];
        throw err;
    });

    cache[cacheKey] = { promise: fetchPromise, time: now };
    const res = await fetchPromise;
    return res.clone();
};
