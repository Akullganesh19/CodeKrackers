'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  MessageSquare,
  Phone,
  BarChart3,
  Scale,
  ShieldCheck,
  Cpu,
  LogOut,
  ChevronRight,
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const navItems = [
  { label: 'Command Center', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'SMS Scanner', icon: MessageSquare, href: '/sms-scanner' },
  { label: 'Call Monitor', icon: Phone, href: '/call-monitor' },
  { label: 'Threat Analytics', icon: BarChart3, href: '/analytics' },
  { label: 'Legal Vault', icon: Scale, href: '/legal' },
  { label: 'Security Posture', icon: ShieldCheck, href: '/security' },
  { label: 'System Architecture', icon: Cpu, href: '/tech-stack' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-[260px] z-40 flex flex-col">
      {/* Glass backdrop */}
      <div className="absolute inset-0 bg-[#0b0b18]/90 backdrop-blur-2xl border-r border-[rgba(124,58,237,0.08)]" />

      {/* Content */}
      <div className="relative flex flex-col h-full">
        {/* Brand */}
        <div className="px-8 pt-10 pb-8 border-b border-[rgba(124,58,237,0.06)]">
          <Link href="/" className="group flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center shadow-lg shadow-[#7c3aed]/20 group-hover:shadow-[#7c3aed]/40 transition-all duration-300">
              <span className="font-space font-black text-white text-sm">◈</span>
            </div>
            <div className="flex flex-col">
              <span className="font-space font-bold text-lg text-white tracking-tight glow-cyber">VSDP</span>
              <span className="font-mono text-[0.4rem] text-[#64748b] uppercase tracking-[0.3em]">Defense Command</span>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item, idx) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 px-5 py-3.5 rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-[rgba(124,58,237,0.1)] text-[#a78bfa]"
                    : "text-[#64748b] hover:bg-[rgba(124,58,237,0.04)] hover:text-[#94a3b8]"
                )}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-gradient-to-b from-[#7c3aed] to-[#0aefff] rounded-full"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}

                <item.icon
                  size={17}
                  className={cn(
                    "transition-colors shrink-0",
                    isActive ? "text-[#a78bfa]" : "text-[#64748b] group-hover:text-[#94a3b8]"
                  )}
                />
                <span className="font-mono text-[0.6rem] uppercase tracking-[0.15em] font-medium">
                  {item.label}
                </span>

                {isActive && (
                  <ChevronRight size={12} className="ml-auto text-[#a78bfa]/60" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* User Profile */}
        <div className="px-6 py-6 border-t border-[rgba(124,58,237,0.06)]">
          <div className="flex items-center gap-3 px-3 py-3 rounded-lg bg-[rgba(124,58,237,0.04)] border border-[rgba(124,58,237,0.06)]">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#7c3aed]/20 to-[#0aefff]/10 border border-[rgba(124,58,237,0.15)] flex items-center justify-center font-space font-bold text-[#a78bfa] text-xs">
              CO
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-mono text-[0.6rem] text-white truncate font-medium">Cyber Officer</div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="pulse-dot lime" style={{ width: 4, height: 4 }} />
                <span className="font-mono text-[0.4rem] text-[#10b981] uppercase tracking-[0.2em]">L3 · Active</span>
              </div>
            </div>
          </div>

          <Link
            href="/"
            className="flex items-center gap-3 px-3 py-3 mt-3 rounded-lg text-[#64748b] hover:text-[#ff2056] hover:bg-[rgba(255,32,86,0.04)] transition-all duration-200 group"
          >
            <LogOut size={14} className="group-hover:rotate-180 transition-transform duration-500" />
            <span className="font-mono text-[0.55rem] uppercase tracking-[0.15em]">Disconnect</span>
          </Link>
        </div>
      </div>
    </aside>
  )
}