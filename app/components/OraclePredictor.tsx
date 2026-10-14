'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'

export default function OraclePredictor() {
  const pathname = usePathname()

  useEffect(() => {
    if (typeof window === 'undefined') return
    if ((window as any).__oracle_initialized) return
    (window as any).__oracle_initialized = true

    console.log("🔮 Oracle: Predictive Intelligence Engine online.")

    const originalFetch = window.fetch
    const predictionCache = new Map<string, { promise: Promise<Response>, time: number }>()

    // Cleanup interval for stale cache entries
    setInterval(() => {
      const now = Date.now()
      for (const [key, value] of predictionCache.entries()) {
        if (now - value.time > 30000) {
          predictionCache.delete(key)
        }
      }
    }, 60000) // run every minute

    // Intercept fetch calls to serve predicted data
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
      const method = init?.method || (input instanceof Request ? input.method : 'GET')

      let cacheKey = url
      if (method === 'POST' && init?.body && typeof init.body === 'string') {
        cacheKey = `${url}|${init.body}`
      } else if (method !== 'GET') {
        return originalFetch(input, init)
      }

      const cached = predictionCache.get(cacheKey)
      // 30 second TTL for predictions
      if (cached && Date.now() - cached.time < 30000) {
        console.log(`🔮 Oracle: Anticipated user action. Zero-latency fetch delivered for ${url.split('/').pop()}`)
        const res = await cached.promise
        predictionCache.delete(cacheKey) // Consume cache once used
        return res.clone()
      }

      return originalFetch(input, init)
    }

    // Expose Oracle API globally
    ;(window as any).oracle = {
      predict: (url: string, init?: RequestInit) => {
        const method = init?.method || 'GET'
        let cacheKey = url
        if (method === 'POST' && init?.body && typeof init.body === 'string') {
          cacheKey = `${url}|${init.body}`
        }

        if (predictionCache.has(cacheKey)) return
        console.log(`🔮 Oracle: Predicting future user need for ${url.split('/').pop()}`)

        const promise = originalFetch(url, init).then(res => {
          return res.arrayBuffer().then(buffer => {
            // Reconstruct headers manually since Headers object stringifies to {}
            const headers: Record<string, string> = {}
            res.headers.forEach((value, key) => {
              headers[key] = value
            })
            return new Response(buffer, {
              status: res.status,
              statusText: res.statusText,
              headers: headers
            })
          })
        }).catch(err => {
          console.error("Oracle prediction failed:", err)
          throw err
        })

        predictionCache.set(cacheKey, { promise, time: Date.now() })
      }
    }
  }, [])

  // Behavioral Routing Predictions
  useEffect(() => {
    if (typeof window === 'undefined' || !(window as any).oracle) return

    const token = localStorage.getItem('vsdp_token') || 'dummy_token'
    const headers = { 'Authorization': `Bearer ${token}` }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    // Scenario: User opens app or is on login, they will almost certainly go to dashboard
    if (pathname === '/' || pathname === '/login') {
      (window as any).oracle.predict(`${apiUrl}/api/analytics/dashboard-summary`, { headers })
    }
  }, [pathname])

  return null
}
