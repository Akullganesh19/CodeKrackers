'use client'

import { useState, useEffect } from 'react'
import { Bell, Search, Settings, Wifi, Shield, Lock } from 'lucide-react'
import Link from 'next/link'

export default function Topbar({ title }: { title: string }) {
  const [time, setTime] = useState('')

  useEffect(() => {
    const update = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }))
    }
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="sticky top-0 z-30">
      {/* Glass backdrop */}
      <div className="absolute inset-0 bg-[#0b0b18]/80 backdrop-blur-2xl border-b border-[rgba(124,58,237,0.06)]" />

      <div className="relative flex items-center justify-between px-10 py-4">
        {/* Left: Title + Search */}
        <div className="flex items-center gap-10">
          <h1 className="font-space text-xl font-bold text-white tracking-tight">
            {title}
          </h1>

          <div className="relative hidden md:block">
            <Search size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#64748b]" />
            <input
              type="text"
              placeholder="Search threats, reports, cases..."
              className="w-72 bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] rounded-lg pl-11 pr-4 py-2.5 font-mono text-[0.6rem] text-[#94a3b8] placeholder:text-[#475569] focus:outline-none focus:border-[rgba(124,58,237,0.3)] focus:ring-1 focus:ring-[rgba(124,58,237,0.15)] transition-all"
            />
          </div>
        </div>

        {/* Right: System Status */}
        <div className="flex items-center gap-8">
          {/* Connection status */}
          <div className="hidden sm:flex items-center gap-3 px-4 py-2 rounded-lg bg-[rgba(10,239,255,0.04)] border border-[rgba(10,239,255,0.08)]">
            <Wifi size={12} className="text-[#0aefff]" />
            <span className="font-mono text-[0.45rem] text-[#0aefff] uppercase tracking-[0.2em] font-semibold">Secure Link</span>
          </div>

          {/* User Clearance */}
          <div className="hidden lg:flex items-center gap-3 px-4 py-2 rounded-lg bg-[rgba(124,58,237,0.04)] border border-[rgba(124,58,237,0.08)]">
            <Lock size={12} className="text-[#a78bfa]" />
            <span className="font-mono text-[0.45rem] text-[#a78bfa] uppercase tracking-[0.2em] font-semibold">L4 Clearance</span>
          </div>

          {/* Clock */}
          <div className="font-mono text-[0.6rem] text-[#94a3b8] tracking-widest tabular-nums">
            {time} <span className="text-[#475569]">UTC+5:30</span>
          </div>

          {/* Notifications */}
          <button className="relative w-9 h-9 rounded-lg bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center hover:border-[rgba(124,58,237,0.25)] transition-all group">
            <Bell size={15} className="text-[#64748b] group-hover:text-[#94a3b8]" />
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#ff2056] flex items-center justify-center font-mono text-[0.35rem] text-white font-bold">3</span>
          </button>

          {/* Settings */}
          <Link href="/settings" className="w-9 h-9 rounded-lg bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center hover:border-[rgba(124,58,237,0.25)] transition-all group">
            <Settings size={15} className="text-[#64748b] group-hover:text-[#94a3b8] group-hover:rotate-90 transition-transform duration-500" />
          </Link>
        </div>
      </div>
    </header>
  )
}