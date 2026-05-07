'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Phone, 
  BarChart3, 
  Scale, 
  ShieldCheck, 
  Settings,
  LogOut,
  Cpu
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'SMS Scanner', icon: MessageSquare, href: '/sms-scanner' },
  { label: 'Call Monitor', icon: Phone, href: '/call-monitor' },
  { label: 'Analytics', icon: BarChart3, href: '/analytics' },
  { label: 'Legal & Compliance', icon: Scale, href: '/legal' },
  { label: 'Security & RBAC', icon: ShieldCheck, href: '/security' },
  { label: 'Tech Stack', icon: Settings, href: '/tech-stack' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-[240px] bg-surface border-r border-white/[0.03] flex flex-col z-40">
      <div className="p-10">
        <Link href="/" className="font-space font-bold text-2xl text-accent tracking-tighter flex flex-col gap-1">
          ◈ VSDP
          <span className="font-mono text-[0.45rem] text-muted tracking-[0.4em] uppercase">Defense Platform</span>
        </Link>
      </div>

      <nav className="flex-1 px-6 space-y-2 mt-10">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-4 py-3.5 transition-all group rounded-md",
                isActive 
                  ? "bg-accent/[0.07] text-accent border-l-2 border-accent" 
                  : "text-muted hover:text-white hover:bg-white/[0.02]"
              )}
            >
              <div className="flex items-center gap-4">
                <item.icon size={18} className={cn("transition-colors", isActive ? "text-accent" : "group-hover:text-accent")} />
                <span className="font-mono text-[0.65rem] uppercase tracking-widest font-light">{item.label}</span>
              </div>
            </Link>
          )
        })}
      </nav>

      <div className="p-8 border-t border-white/[0.03] space-y-8">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center font-space font-bold text-accent">
            CO
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="font-mono text-[0.7rem] text-white truncate">Cyber Officer</div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="font-mono text-[0.45rem] text-accent uppercase tracking-widest">L3 Access</span>
            </div>
          </div>
        </div>

        <Link href="/" className="flex items-center gap-3 font-mono text-[0.6rem] text-muted hover:text-danger uppercase tracking-widest transition-colors group">
          <LogOut size={14} className="group-hover:rotate-180 transition-transform duration-500" />
          Sign Out
        </Link>
      </div>
    </aside>
  )
}
