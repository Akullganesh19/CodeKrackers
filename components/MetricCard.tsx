'use client'

import { useState, useEffect } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: number
  prefix?: string
  suffix?: string
  trend: string
  isPositive: boolean
  color: 'accent' | 'danger' | 'warning' | 'success'
  icon: React.ReactNode
}

export default function MetricCard({ label, value, prefix = '', suffix = '', trend, isPositive, color, icon }: MetricCardProps) {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    // Simple count animation
    let start = 0
    const end = value
    const duration = 2000
    const increment = end / (duration / 16)
    
    const timer = setInterval(() => {
      start += increment
      if (start >= end) {
        setCount(end)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, 16)

    return () => clearInterval(timer)
  }, [value])

  const colorMap = {
    accent: 'text-accent',
    danger: 'text-danger',
    warning: 'text-warning',
    success: 'text-success'
  }

  const borderMap = {
    accent: 'border-accent/20',
    danger: 'border-danger/20',
    warning: 'border-warning/20',
    success: 'border-success/20'
  }

  const bgMap = {
    accent: 'bg-accent/5',
    danger: 'bg-danger/5',
    warning: 'bg-warning/5',
    success: 'bg-success/5'
  }

  return (
    <div className="vsdp-card p-8 space-y-6 relative group overflow-hidden">
      <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity ${colorMap[color]}`}>
        {icon}
      </div>

      <div className="space-y-2">
        <div className="font-mono text-[0.55rem] text-muted uppercase tracking-[0.3em]">{label}</div>
        <div className="flex items-baseline gap-2">
          <div className={`font-space text-4xl font-bold tracking-tight ${colorMap[color]}`}>
            {prefix}{count.toLocaleString()}{suffix}
          </div>
          <div className={`flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[0.6rem] ${isPositive ? 'text-success bg-success/10' : 'text-danger bg-danger/10'}`}>
            {isPositive ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
            {trend}
          </div>
        </div>
      </div>

      <div className="w-full h-1 bg-white/[0.03] rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: '70%' }}
          transition={{ duration: 1, delay: 0.5 }}
          className={`h-full ${color === 'accent' ? 'bg-accent' : color === 'danger' ? 'bg-danger' : color === 'warning' ? 'bg-warning' : 'bg-success'}`}
        />
      </div>
    </div>
  )
}
