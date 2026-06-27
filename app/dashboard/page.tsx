'use client'

import { useState, useEffect, useCallback } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import OpenClawStatus from '@/components/OpenClawStatus'
import { motion, AnimatePresence } from 'framer-motion'
import { dedupedFetch } from '@/app/lib/api'
import {
  ShieldAlert,
  Users,
  Zap,
  Clock,
  ArrowUpRight,
  ChevronRight,
  Activity,
  Maximize2,
  Lock,
  Globe,
  Database,
  Cpu,
  RefreshCcw,
  AlertCircle
} from 'lucide-react'

// --- HELPER COMPONENTS ---

function Sparkline({ color = '#c4b5fd' }: { color?: string }) {
  const [pathData, setPathData] = useState("")

  useEffect(() => {
    const points = Array.from({ length: 15 }).map(() => Math.random() * 40 + 10)
    const data = `M 0 ${points[0]} ${points.map((p, i) => `L ${i * 10} ${p}`).join(' ')}`
    setPathData(data)
  }, [])

  if (!pathData) return <div className="h-8" />

  return (
    <svg className="w-full h-8 overflow-visible">
      <motion.path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 2, ease: "easeInOut" }}
      />
    </svg>
  )
}

function GridMap() {
  const [hotspots, setHotspots] = useState<any[]>([])

  useEffect(() => {
    const newHotspots = Array.from({ length: 12 }).map(() => ({
      left: `${10 + Math.random() * 80}%`,
      top: `${10 + Math.random() * 80}%`,
      duration: 2 + Math.random() * 3,
      delay: Math.random() * 2
    }))
    setHotspots(newHotspots)
  }, [])

  return (
    <div className="relative w-full h-[500px] bg-white/[0.01] border border-white/5 rounded-lg overflow-hidden group">
      <div className="absolute inset-0 grid grid-cols-20 grid-rows-15 gap-0 opacity-20">
        {Array.from({ length: 300 }).map((_, i) => (
          <div key={i} className="border-[0.5px] border-white/10" />
        ))}
      </div>

      {/* Simulated Threat Hotspots */}
      <div className="absolute inset-0">
        {hotspots.map((spot, i) => (
          <motion.div
            key={i}
            className="absolute w-4 h-4 rounded-full bg-accent/40 blur-xl"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.2, 0.5, 0.2]
            }}
            transition={{
              duration: spot.duration,
              repeat: Infinity,
              delay: spot.delay
            }}
            style={{
              left: spot.left,
              top: spot.top
            }}
          />
        ))}
      </div>

      <div className="absolute top-8 left-10 space-y-2">
        <h3 className="font-space text-2xl font-black text-white/40 uppercase italic tracking-tighter">Live Threat Topology</h3>
        <div className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.4em]">Sector Grid India_Core_01</div>
      </div>

      <div className="absolute bottom-8 right-10 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          <span className="font-mono text-[0.5rem] text-accent uppercase tracking-widest">Active Node</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-danger" />
          <span className="font-mono text-[0.5rem] text-danger uppercase tracking-widest">Critical Breach</span>
        </div>
      </div>
    </div>
  )
}

import Link from 'next/link'

function CommandMetric({ label, val, sub, trend, href, colorClass = "text-accent" }: any) {
  const content = (
    <div className={`vsdp-card p-6 flex flex-col justify-between group h-40 transition-all ${href ? 'hover:border-accent/40 hover:bg-accent/5 cursor-pointer' : ''}`}>
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <div className="font-space text-3xl font-black">{val}</div>
          <div className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.2em]">{label}</div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className={`font-mono text-[0.45rem] font-bold ${trend.startsWith('+') ? 'text-success' : 'text-danger'}`}>
            {trend}
          </div>
          {href && <ArrowUpRight size={10} className="text-accent opacity-0 group-hover:opacity-100 transition-opacity" />}
        </div>
      </div>
      <div className="space-y-4">
        <Sparkline color={colorClass === 'text-accent' ? '#c4b5fd' : colorClass === 'text-danger' ? '#ff3c6e' : '#7fff6e'} />
        <div className="font-mono text-[0.45rem] text-muted/40 uppercase tracking-widest">{sub}</div>
      </div>
    </div>
  )

  if (href) return <Link href={href}>{content}</Link>
  return content
}

export default function Dashboard() {
  const [mounted, setMounted] = useState(false)
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<any>(null)
  const [selectedSector, setSelectedSector] = useState('01')

  useEffect(() => {
    setMounted(true)
    // Fallback mock data when backend is unavailable
    const mockSummary = {
      stats: {
        smishing: 1847,
        vishing: 342,
        crypto_scam: 156,
        firs_filed: 89,
        protected_users: 12453,
        total_threats: 2400000,
      },
      trends: {
        smishing_today: 127,
        vishing_today: 23,
      },
      avg_confidence: 0.91,
      recent_detections: [
        { source: '91+9876543210', type: 'SMISHING', severity: 'HIGH', confidence: 0.94, timestamp: new Date().toISOString() },
        { source: '91+9123456789', type: 'VISHING', severity: 'CRITICAL', confidence: 0.97, timestamp: new Date().toISOString() },
        { source: '91+9988776655', type: 'CRYPTO_SCAM', severity: 'MEDIUM', confidence: 0.82, timestamp: new Date().toISOString() },
        { source: '91+9876501234', type: 'SMISHING', severity: 'HIGH', confidence: 0.88, timestamp: new Date().toISOString() },
        { source: '91+9123450987', type: 'SMISHING', severity: 'LOW', confidence: 0.65, timestamp: new Date().toISOString() },
      ],
    }

    async function fetchSummary() {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null
        const res = await dedupedFetch('http://localhost:8000/api/analytics/dashboard-summary', {
          headers: { 'Authorization': `Bearer ${token || 'dummy_token'}` }
        })
        if (res.ok) {
          const data = await res.json()
          setSummary(data)
        } else {
          // Use mock data if response is not ok
          setSummary(mockSummary)
        }
      } catch (err) {
        // Silently swallow the fetch error so Next.js doesn't trigger any error overlays
        setSummary(mockSummary)
      } finally {
        setLoading(false)
      }
    }
    fetchSummary()
    const interval = setInterval(fetchSummary, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500)
    return () => clearTimeout(timer)
  }, [])

  if (!mounted) return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
      <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.5em] animate-pulse">Syncing_Command_Center...</div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-bg text-white selection:bg-accent/20">
      <Sidebar />
      <main className="flex-1 ml-[240px]">

        {/* CINEMATIC HEADER */}
        <header className="h-[100px] border-b border-white/[0.03] bg-bg/50 backdrop-blur-xl px-12 flex items-center justify-between sticky top-0 z-50">
          <div className="flex items-center gap-10">
            <h1 className="font-space text-3xl font-black uppercase tracking-tighter">VSDP command_center</h1>
            <div className="h-6 w-px bg-white/10" />
            <div className="flex gap-8">
              {[
                { label: 'Total Intercepts', val: loading ? '---' : summary?.stats?.total_threats || '2.4M', icon: <Globe size={12} /> },
                { label: 'Network Load', val: '42%', icon: <Activity size={12} /> },
                { label: 'Threat Index', val: loading ? 'Stable' : (summary?.stats?.smishing || 0) > 100 ? 'Critical' : 'Stable', icon: <AlertCircle size={12} className={loading ? 'text-success' : (summary?.stats?.smishing || 0) > 100 ? 'text-danger' : 'text-success'} /> }
              ].map((item, i) => (
                <div key={i} className="flex flex-col gap-1">
                  <div className="flex items-center gap-2 font-mono text-[0.5rem] text-muted uppercase tracking-widest">
                    {item.icon} {item.label}
                  </div>
                  <div className="font-space text-sm font-bold tracking-tight">{item.val}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button className="p-3 bg-white/[0.03] border border-white/5 rounded-full hover:bg-accent/10 hover:border-accent/20 transition-all">
              <RefreshCcw size={18} className="text-accent" />
            </button>
            <div className="w-12 h-12 bg-accent/10 border border-accent/40 flex items-center justify-center font-space font-bold text-accent">
              B1
            </div>
          </div>
        </header>

        <div className="p-10 grid grid-cols-1 lg:grid-cols-12 gap-10">

          {/* LEFT COLUMN (2/3) */}
          <div className="lg:col-span-8 space-y-10">

            {/* METRICS GRID */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <CommandMetric label="Detection Rate" val={`${((summary?.avg_confidence || 0.91) * 100).toFixed(0)}%`} sub="Accuracy (± 0.2%)" trend="+4.1%" />
              <CommandMetric label="Smishing Detected" val={summary?.stats?.smishing || '0'} sub="SMS Threats" trend={`+${summary?.trends?.smishing_today || 0}`} />
              <CommandMetric label="Vishing Detected" val={summary?.stats?.vishing || '0'} sub="Voice Threats" trend={`+${summary?.trends?.vishing_today || 0}`} colorClass="text-danger" />
              <CommandMetric label="Firs Filed" val={summary?.stats?.firs_filed || '0'} sub="Legal Actions" trend="+2" colorClass="text-success" />
              <CommandMetric label="Protected Users" val={summary?.stats?.protected_users || '0'} sub="Active Nodes" trend="+12" />
              <CommandMetric label="Threat Level" val={`${((summary?.stats?.total_threats || 0) / 100).toFixed(1)}%`} sub="Regional Intensity" trend="+5.4%" colorClass="text-danger" />
            </div>

            {/* LARGE GRID MAP */}
            <GridMap />
          </div>

          {/* RIGHT COLUMN (1/3) */}
          <div className="lg:col-span-4 space-y-10">

            {/* SNAPSHOT PANEL */}
            <div className="vsdp-card p-10 space-y-8">
              <div className="flex justify-between items-center">
                <h3 className="font-space text-lg font-bold uppercase tracking-tight">System Snapshot</h3>
                <Maximize2 size={16} className="text-muted cursor-pointer hover:text-white transition-colors" />
              </div>

              <div className="grid grid-cols-5 gap-2 h-20">
                {[
                  { val: '4.3', label: 'CPU', active: true },
                  { val: '86%', label: 'MEM', active: false },
                  { val: '24k', label: 'THRD', active: false },
                  { val: '135', label: 'DISK', active: false },
                  { val: '94', label: 'NET', active: false },
                ].map((item, i) => (
                  <div key={i} className={`flex flex-col items-center justify-center gap-1 border border-white/5 rounded transition-all cursor-pointer ${item.active ? 'bg-accent/10 border-accent/40 shadow-[0_0_20px_rgba(196,181,253,0.1)]' : 'hover:bg-white/[0.02]'}`}>
                    <div className={`font-space text-xs font-bold ${item.active ? 'text-accent' : 'text-white/60'}`}>{item.val}</div>
                    <div className="font-mono text-[0.4rem] text-muted/40 uppercase">{item.label}</div>
                  </div>
                ))}
              </div>

              {/* HEALTH GAUGE */}
              <div className="space-y-6 pt-6 border-t border-white/5">
                <div className="flex justify-between items-end">
                  <div className="space-y-1">
                    <div className="font-space text-lg font-bold">Health Rate</div>
                    <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest italic">Cumulative system integrity</div>
                  </div>
                  <div className="font-space text-3xl font-black text-accent">4.7</div>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-accent"
                    initial={{ width: 0 }}
                    animate={{ width: '94%' }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
                </div>
              </div>
            </div>

            {/* OPENCLAW GATEWAY */}
            <OpenClawStatus />

            {/* LIVE ACTIVITY TABLE */}
            <div className="vsdp-card p-0 overflow-hidden">
              <div className="p-8 border-b border-white/[0.03]">
                <h3 className="font-space text-lg font-bold uppercase tracking-tight">Threat Flow</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/[0.03] bg-white/[0.01]">
                      <th className="px-8 py-4 text-left font-mono text-[0.45rem] text-muted uppercase tracking-widest">Zone</th>
                      <th className="px-8 py-4 text-left font-mono text-[0.45rem] text-muted uppercase tracking-widest">Intensity</th>
                      <th className="px-8 py-4 text-right font-mono text-[0.45rem] text-muted uppercase tracking-widest">Avg_Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.03]">
                    {(summary?.recent_detections || []).map((row: any, i: number) => (
                      <tr key={i} className="hover:bg-accent/[0.02] transition-colors group">
                        <td className="px-8 py-5 font-mono text-[0.6rem] text-white/60 group-hover:text-white truncate max-w-[100px]">{row.source}</td>
                        <td className="px-8 py-5 font-mono text-[0.6rem] text-accent font-bold uppercase">{row.type}</td>
                        <td className="px-8 py-5 text-right font-mono text-[0.55rem] text-muted">{row.severity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* SYSTEM STATUS */}
            <div className="flex items-center justify-center gap-6 pt-4">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                <span className="font-mono text-[0.5rem] text-muted uppercase tracking-widest italic">Sovereign_OS v4.2.1</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-success" />
                <span className="font-mono text-[0.5rem] text-muted uppercase tracking-widest italic">L3 Authorized</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx global>{`
        .grid-cols-20 { grid-template-columns: repeat(20, minmax(0, 1fr)); }
        .grid-rows-15 { grid-template-rows: repeat(15, minmax(0, 1fr)); }
      `}</style>
    </div>
  )
}
