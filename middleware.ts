import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

// Mapping of protected routes to the roles allowed to access them
const RBAC_CONFIG: Record<string, string[]> = {
  '/dashboard/verification': ['bank', 'officer', 'admin', 'superadmin'],
  '/dashboard/investigation': ['officer', 'admin', 'superadmin'],
  '/dashboard/firs': ['officer', 'admin', 'superadmin'],
  '/dashboard/users': ['admin', 'superadmin'],
  '/dashboard/settings': ['superadmin'],
}

const encoder = new TextEncoder()

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('vsdp_token')?.value
  const { pathname } = request.nextUrl

  if (pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }

    try {
      const jwtSecret = process.env.JWT_SECRET
      if (!jwtSecret) {
        console.error('CRITICAL: JWT_SECRET is missing in .env! Authentication will fail.')
        return NextResponse.redirect(new URL('/login', request.url))
      }

      const secret = encoder.encode(jwtSecret)
      const { payload } = await jwtVerify(token, secret)
      const userRole = payload.role as string

      // Enforce clearance levels for restricted sub-sections
      for (const [route, allowedRoles] of Object.entries(RBAC_CONFIG)) {
        if (pathname.startsWith(route) && !allowedRoles.includes(userRole)) {
          // Unauthorized role: Redirect back to the main dashboard overview
          return NextResponse.redirect(new URL('/dashboard', request.url))
        }
      }
      
      return NextResponse.next()
    } catch (error) {
      // Token invalid or expired: force re-authentication
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

// Only run middleware on dashboard paths
export const config = {
  matcher: ['/dashboard/:path*'],
}