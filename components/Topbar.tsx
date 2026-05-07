'use client'

import { useState, useEffect } from 'react'
import { Bell, Search, Command } from 'lucide-react'

export default function Topbar({ title }: { title: string }) {
  const [time, setTime] = useState<Date | null>(null)

  useEffect(() => {
    setTime(new Date())
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-[80px] border-b border-white/[0.03] flex items-center justify-between px-12 bg-bg/50 backdrop-blur-xl sticky top-0 z-30">
      <div className="flex items-center gap-6">
        <div className="h-4 w-[1px] bg-accent/30" />
        <h2 className="font-space font-bold text-xl text-white tracking-tight uppercase">{title}</h2>
      </div>

      <div className="flex items-center gap-10">
        <div className="flex items-center gap-3 px-4 py-1.5 rounded-full bg-success/5 border border-success/20">
          <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
          <span className="font-mono text-[0.55rem] text-success uppercase tracking-[0.4em]">Live_System_Active</span>
        </div>

        <div className="flex flex-col items-end">
          <div className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.4em]">System_Time</div>
          <div className="font-mono text-[0.65rem] text-accent tracking-widest uppercase">
            {time ? time.toLocaleTimeString() : '--:--:--'}
          </div>
        </div>

        <div className="flex items-center gap-6 border-l border-white/[0.03] pl-10">
          <button className="relative w-10 h-10 rounded-full border border-white/5 flex items-center justify-center hover:bg-white/5 transition-colors">
             <Bell size={16} className="text-muted" />
             <span className="absolute top-2.5 right-2.5 w-1.5 h-1.5 bg-danger rounded-full border-2 border-bg" />
          </button>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-mono text-[0.55rem] text-white uppercase tracking-widest">Operator</div>
              <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest italic">BHARATH_S</div>
            </div>
            <div className="w-10 h-10 rounded-full border border-accent/20 bg-accent/5 flex items-center justify-center font-space font-bold text-accent text-xs">
               BS
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
