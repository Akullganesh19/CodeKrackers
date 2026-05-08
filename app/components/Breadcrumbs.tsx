'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Home } from 'lucide-react'

export default function Breadcrumbs() {
  const pathname = usePathname()
  const pathSegments = pathname.split('/').filter((segment) => segment !== '')

  return (
    <nav className="flex items-center space-x-2 font-mono text-[0.55rem] uppercase tracking-[0.2em] text-[#64748b] mb-8">
      <Link href="/" className="hover:text-white transition-all hover:scale-110">
        <Home size={12} />
      </Link>
      
      {pathSegments.map((segment, index) => {
        const href = `/${pathSegments.slice(0, index + 1).join('/')}`
        const isLast = index === pathSegments.length - 1
        
        // Map segment IDs to high-tech display names
        const labels: Record<string, string> = {
          dashboard: 'Command Center',
          report: 'Threat Intel',
          verification: 'Fraud Audit',
          investigation: 'Deep Trace',
          firs: 'Legal FIRs',
          users: 'Personnel',
          settings: 'Grid Config'
        }
        
        const label = labels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)

        return (
          <div key={href} className="flex items-center space-x-2">
            <ChevronRight size={10} className="text-[#475569]" />
            {isLast ? (
              <span className="text-[#a78bfa] drop-shadow-[0_0_8px_rgba(167,139,250,0.3)]">{label}</span>
            ) : (
              <Link href={href} className="hover:text-white transition-colors">
                {label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}