'use client'

let isInitialized = false

export function PhantomProvider() {
  if (typeof window !== 'undefined' && !isInitialized) {
    isInitialized = true
    const originalFetch = window.fetch

    const inFlight = new Map<string, Promise<Response>>()
    // Cache storing promises of responses to allow independent consumption and prevent memory bloat/streaming breakage.
    // Also store timestamps to invalidate correctly based on cache headers if possible, or fallback TTL.
    const cache = new Map<string, { resPromise: Promise<Response>, timestamp: number }>()

    const FALLBACK_TTL = 30000 // 30 seconds

    window.fetch = function(input, init) {
      let method = 'GET'
      let cacheControl = ''

      if (init && init.method) {
        method = init.method.toUpperCase()
      } else if (input instanceof Request && input.method) {
        method = input.method.toUpperCase()
      }

      let url = ''
      if (typeof input === 'string') {
        url = input
      } else if (input instanceof URL) {
        url = input.toString()
      } else if (input instanceof Request) {
        url = input.url
        // Don't cache if explicit no-store is passed
        cacheControl = input.headers.get('Cache-Control') || ''
      }

      if (init && init.headers) {
         const h = new Headers(init.headers)
         cacheControl = h.get('Cache-Control') || cacheControl
      }

      // 1. Only cache/coalesce GET requests that aren't explicitly no-store
      if (method !== 'GET' || cacheControl.includes('no-store') || cacheControl.includes('no-cache')) {
        return originalFetch.call(this, input, init)
      }

      // 2. Cache Layer
      const cached = cache.get(url)
      if (cached && Date.now() - cached.timestamp < FALLBACK_TTL) {
        return cached.resPromise.then(res => res.clone())
      }

      // 3. Request Coalescing (In-flight dedup)
      if (inFlight.has(url)) {
        return inFlight.get(url)!.then(res => res.clone())
      }

      // 4. Make Request and populate cache/in-flight
      const promise = originalFetch.call(this, input, init).then((res) => {
        if (res.ok) {
          // If the server explicitly says no-store in response, we shouldn't have cached it,
          // but we only know that after. We can remove it from cache here.
          const resCacheControl = res.headers.get('Cache-Control') || ''
          if (resCacheControl.includes('no-store') || resCacheControl.includes('no-cache')) {
            cache.delete(url)
          }
        } else {
            // Don't cache failed responses
            cache.delete(url)
        }
        return res
      }).catch(err => {
          cache.delete(url)
          throw err
      }).finally(() => {
        inFlight.delete(url)
      })

      // Store a clone-generator promise in cache so future cache hits don't consume the same body stream
      const cacheablePromise = promise.then(res => res.clone())

      cache.set(url, {
        resPromise: cacheablePromise,
        timestamp: Date.now()
      })
      inFlight.set(url, cacheablePromise)

      return promise
    }
  }

  return null
}
