'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'

const Corner = ({ className }: { className?: string }) => (
  <svg width="10" height="10" viewBox="0 0 10 10" fill="none" className={`absolute ${className} opacity-30 group-hover:opacity-100 transition-all duration-500`}>
    <path d="M0 0H8V2H2V8H0V0Z" fill="currentColor" />
  </svg>
)

interface MetricCardProps {
  label: string
  value: number | string
  suffix?: string
  trend?: string
  isPositive?: boolean
  color: 'cyber' | 'neon' | 'alert' | 'amber' | 'lime'
  icon?: ReactNode
}

const colorMap = {
  cyber: {
    bg: 'bg-[rgba(124,58,237,0.08)]',
    border: 'border-[rgba(124,58,237,0.15)]',
    text: 'text-[#a78bfa]',
    glow: 'shadow-[#7c3aed]/20',
  },
  neon: {
    bg: 'bg-[rgba(10,239,255,0.06)]',
    border: 'border-[rgba(10,239,255,0.12)]',
    text: 'text-[#0aefff]',
    glow: 'shadow-[#0aefff]/15',
  },
  alert: {
    bg: 'bg-[rgba(255,32,86,0.08)]',
    border: 'border-[rgba(255,32,86,0.15)]',
    text: 'text-[#ff2056]',
    glow: 'shadow-[#ff2056]/20',
  },
  amber: {
    bg: 'bg-[rgba(245,158,11,0.08)]',
    border: 'border-[rgba(245,158,11,0.15)]',
    text: 'text-[#f59e0b]',
    glow: 'shadow-[#f59e0b]/20',
  },
  lime: {
    bg: 'bg-[rgba(16,185,129,0.08)]',
    border: 'border-[rgba(16,185,129,0.15)]',
    text: 'text-[#10b981]',
    glow: 'shadow-[#10b981]/20',
  },
}

export default function MetricCard({ label, value, suffix, trend, isPositive, color, icon }: MetricCardProps) {
  const c = colorMap[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative p-8 flex flex-col gap-6 overflow-hidden group bg-[#0b0b18]/60 border border-[rgba(124,58,237,0.1)] hover:border-[rgba(124,58,237,0.4)] transition-all duration-500 rounded-none shadow-2xl"
    >
      {/* Technical Corners */}
      <Corner className="top-2 left-2 text-[#a78bfa]" />
      <Corner className="top-2 right-2 rotate-90 text-[#a78bfa]" />
      <Corner className="bottom-2 left-2 -rotate-90 text-[#a78bfa]" />
      <Corner className="bottom-2 right-2 rotate-180 text-[#a78bfa]" />

      {/* Scanning Line Animation */}
      <motion.div
        animate={{ y: ['-150%', '300%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        className="absolute inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-[#7c3aed]/20 to-transparent z-0"
      />

      {/* Subtle glow on hover */}
      <div className={`absolute -inset-10 bg-[radial-gradient(circle_at_50%_0%,${color === 'cyber' ? '#7c3aed' : '#0aefff'},transparent_50%)] opacity-0 group-hover:opacity-10 transition-opacity duration-700 blur-3xl`} />

      {/* Top row */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[0.55rem] text-[#64748b] uppercase tracking-[0.2em] font-medium">{label}</span>
        {icon && (
          <div className={`w-9 h-9 rounded-lg ${c.bg} border ${c.border} flex items-center justify-center ${c.text}`}>
            {icon}
          </div>
        )}
      </div>

      {/* Value */}
      <div className="flex items-end gap-2">
        <span className={`font-space text-4xl font-black tracking-tight ${c.text} glow-${color === 'cyber' ? 'cyber' : color === 'neon' ? 'neon' : color === 'alert' ? 'alert' : c.text}`}>
          {value}
        </span>
        {suffix && (
          <span className={`font-mono text-[0.65rem] ${c.text} mb-1.5`}>{suffix}</span>
        )}
      </div>

      {/* Trend */}
      {trend && (
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-[0.45rem] font-mono uppercase tracking-widest font-bold ${
            isPositive
              ? 'bg-[rgba(16,185,129,0.1)] text-[#10b981] border border-[rgba(16,185,129,0.15)]'
              : 'bg-[rgba(255,32,86,0.1)] text-[#ff2056] border border-[rgba(255,32,86,0.15)]'
          }`}>
            {isPositive ? '↑' : '↓'} {trend}
          </span>
          <span className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-widest">vs last period</span>
        </div>
      )}
    </motion.div>
  )
}