'use client'

import { useEffect, useRef } from 'react'
import { usePathname } from 'next/navigation'

// Intelligent Route Data Map
// Maps routes to the API endpoints they need, allowing for early data fetching.
const routeDataMap: Record<string, string[]> = {
  '/dashboard': ['/api/analytics/dashboard-summary', '/api/analytics/threat_map'],
  '/analytics': ['/api/analytics/dashboard-summary', '/api/analytics/threat_map'],
  '/dashboard/report': [],
}

export default function PredictiveEngine() {
  const pathname = usePathname()
  const prefetchedUrls = useRef<Set<string>>(new Set())

  // Helper to determine the API base URL dynamically based on current origin,
  // falling back to http://localhost:8000 for local dev if not configured differently.
  const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
      // If we're already on localhost but maybe a different port like 3000,
      // the backend is currently hardcoded to 8000 elsewhere in the app.
      // But we'll try to use a relative or environment-based path if available.
      return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    }
    return 'http://localhost:8000';
  }

  // Strategy 1: Session Warm-up & Next-Action Prediction based on Route
  // When a user lands on a key page (e.g. login or root), we anticipate their next move
  useEffect(() => {
    const prefetchData = async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null

      // Do not attempt to prefetch authenticated routes if no token exists
      if (!token) return;

      const headers = { 'Authorization': `Bearer ${token}` }
      const baseUrl = getApiBaseUrl()

      let urlsToFetch: string[] = []

      // If user is at root or login, prefetch dashboard data as it's the primary next step
      if (pathname === '/' || pathname === '/login') {
         urlsToFetch = routeDataMap['/dashboard'] || []
      } else if (pathname && routeDataMap[pathname]) {
         urlsToFetch = routeDataMap[pathname]
      }

      for (const url of urlsToFetch) {
        if (!prefetchedUrls.current.has(url)) {
           try {
             // Dispatch a silent background fetch.
             fetch(`${baseUrl}${url}`, { headers, cache: 'force-cache' }).catch(() => {})
             prefetchedUrls.current.add(url)
           } catch {
             // Silent fail for predictions
           }
        }
      }
    }

    prefetchData()
  }, [pathname])

  // Strategy 2: Global Link Hover Intent Prediction
  useEffect(() => {
    const handleMouseOver = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest('a')
      if (!target || !target.href) return

      try {
        const url = new URL(target.href)
        // Ensure it's an internal link
        if (url.origin === window.location.origin) {
          const path = url.pathname

          if (routeDataMap[path]) {
            const token = localStorage.getItem('vsdp_token')
            if (!token) return; // Skip if unauthenticated

            const headers = { 'Authorization': `Bearer ${token}` }
            const baseUrl = getApiBaseUrl()

            routeDataMap[path].forEach(apiUrl => {
              if (!prefetchedUrls.current.has(apiUrl)) {
                fetch(`${baseUrl}${apiUrl}`, { headers, cache: 'force-cache' }).catch(() => {})
                prefetchedUrls.current.add(apiUrl)
              }
            })
          }
        }
      } catch {
        // Ignore parsing errors for invalid hrefs
      }
    }

    document.addEventListener('mouseover', handleMouseOver, { passive: true })
    return () => document.removeEventListener('mouseover', handleMouseOver)
  }, [])

  return null
}
