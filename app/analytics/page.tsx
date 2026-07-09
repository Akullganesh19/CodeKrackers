'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { phantomFetch } from '../lib/fetch'
import { 
  BarChart3, 
  Globe, 
  MapPin, 
  TrendingUp, 
  PieChart, 
  ArrowUpRight,
  Filter,
  Download,
  Calendar
} from 'lucide-react'

import { useState, useEffect } from 'react'

export default function Analytics() {
  const [mounted, setMounted] = useState(false)
  const [summary, setSummary] = useState<any>(null)
  const [threatMap, setThreatMap] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setMounted(true)
    async function fetchData() {
      try {
        const token = localStorage.getItem('vsdp_token') || 'dummy_token'
        const [summaryRes, mapRes] = await Promise.all([
          phantomFetch('http://localhost:8000/api/analytics/dashboard-summary', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          phantomFetch('http://localhost:8000/api/analytics/threat_map', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ])
        
        if (summaryRes.ok) setSummary(await summaryRes.json())
        if (mapRes.ok) setThreatMap(await mapRes.json())
      } catch (err) {
        // Silent fallback
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (!mounted) return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
      <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.5em] animate-pulse">Aggregating_Threat_Data...</div>
    </div>
  )

  const attackTimeline = [
    { label: '00:00', val: 120 },
    { label: '04:00', val: 40 },
    { label: '08:00', val: 280 },
    { label: '12:00', val: 420 },
    { label: '16:00', val: 560 },
    { label: '20:00', val: 340 },
  ]

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Advanced Intelligence Analytics" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* HEADER ACTIONS */}
          <div className="flex justify-between items-end">
            <div className="space-y-3">
              <div className="section-tag">Telemetry Data</div>
              <h1 className="font-space text-4xl tracking-tighter uppercase">Threat Intel Heatmap</h1>
            </div>
            <div className="flex gap-6">
              <button className="btn-ghost flex items-center gap-3 py-3 px-6 text-[0.6rem] uppercase tracking-widest">
                <Calendar size={14} /> Last 30 Days
              </button>
              <button className="btn-ghost flex items-center gap-3 py-3 px-6 text-[0.6rem] uppercase tracking-widest">
                <Filter size={14} /> Filter Source
              </button>
              <button className="btn-primary flex items-center gap-3 py-3 px-6 text-[0.6rem] uppercase tracking-widest">
                <Download size={14} /> Export Report
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* GEOGRAPHIC HEATMAP MOCK */}
            <div className="lg:col-span-8 vsdp-card p-10 space-y-10 relative overflow-hidden">
               <div className="flex justify-between items-center">
                 <h3 className="font-space text-xl tracking-tight uppercase">National Scam Distribution</h3>
                 <div className="flex items-center gap-6">
                   <div className="flex items-center gap-2">
                     <div className="w-2 h-2 rounded-full bg-danger" />
                     <span className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">High Alert</span>
                   </div>
                   <div className="flex items-center gap-2">
                     <div className="w-2 h-2 rounded-full bg-warning" />
                     <span className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Medium</span>
                   </div>
                 </div>
               </div>

               <div className="aspect-[16/9] bg-white/[0.02] border border-white/5 rounded-lg flex items-center justify-center relative group">
                  {/* Fake Map Elements */}
                  <div className="absolute inset-0 opacity-20 pointer-events-none overflow-hidden">
                    <div className="absolute top-1/4 left-1/3 w-32 h-32 bg-danger/40 rounded-full blur-[60px] animate-pulse" />
                    <div className="absolute bottom-1/3 right-1/4 w-40 h-40 bg-accent/40 rounded-full blur-[80px]" />
                    <div className="absolute top-1/2 right-1/2 w-24 h-24 bg-warning/40 rounded-full blur-[50px] animate-pulse" />
                  </div>
                  
                  <Globe size={120} className="text-white/5 group-hover:text-accent/10 transition-colors duration-1000" />
                  
                  <div className="absolute top-20 left-1/3 cursor-pointer">
                    <div className="w-3 h-3 bg-danger rounded-full animate-ping absolute" />
                    <div className="w-3 h-3 bg-danger rounded-full relative" />
                    <div className="bg-bg/90 border border-danger/30 p-2 rounded mt-2 font-mono text-[0.5rem] uppercase tracking-widest whitespace-nowrap">Bengaluru (High)</div>
                  </div>

                  <div className="absolute bottom-40 right-1/4 cursor-pointer">
                    <div className="w-3 h-3 bg-accent rounded-full animate-ping absolute" />
                    <div className="w-3 h-3 bg-accent rounded-full relative" />
                    <div className="bg-bg/90 border border-accent/30 p-2 rounded mt-2 font-mono text-[0.5rem] uppercase tracking-widest whitespace-nowrap">Mumbai (Active)</div>
                  </div>

                  <div className="absolute top-1/2 left-1/2 cursor-pointer">
                    <div className="w-3 h-3 bg-warning rounded-full animate-ping absolute" />
                    <div className="w-3 h-3 bg-warning rounded-full relative" />
                    <div className="bg-bg/90 border border-warning/30 p-2 rounded mt-2 font-mono text-[0.5rem] uppercase tracking-widest whitespace-nowrap">Delhi (Monitor)</div>
                  </div>
                  
                  <div className="absolute bottom-6 right-8 font-mono text-[0.5rem] text-muted/40 uppercase tracking-[0.4em] italic">
                    Data Source: CERT-In Live Feed & Citizen Reporting
                  </div>
               </div>
            </div>

            {/* TOP TARGETED CITIES */}
            <div className="lg:col-span-4 vsdp-card p-0 overflow-hidden flex flex-col">
               <div className="p-10 border-b border-white/[0.03]">
                 <h3 className="font-space text-xl tracking-tight uppercase">Top 10 Districts</h3>
               </div>
               <div className="flex-1 overflow-y-auto">
                 <table className="w-full">
                    <tbody className="divide-y divide-white/[0.03]">
                      {threatMap.length > 0 ? threatMap.map((d, i) => (
                        <tr key={i} className="group hover:bg-white/[0.01]">
                          <td className="px-10 py-6">
                            <div className="flex items-center gap-4">
                              <span className="font-mono text-[0.6rem] text-muted">{i+1}</span>
                              <span className="font-mono text-[0.7rem] uppercase tracking-widest">{d.city}</span>
                            </div>
                          </td>
                          <td className="px-10 py-6 text-right">
                            <span className={`font-space font-bold ${d.percentage > 30 ? 'text-danger' : d.percentage > 15 ? 'text-warning' : 'text-success'}`}>
                              {d.threats.toLocaleString()}
                            </span>
                          </td>
                        </tr>
                      )) : (
                        <tr>
                          <td colSpan={2} className="px-10 py-10 text-center font-mono text-[0.6rem] text-muted uppercase">
                            {loading ? "Loading..." : "No data available"}
                          </td>
                        </tr>
                      )}
                    </tbody>
                 </table>
               </div>
               <div className="p-8 bg-accent/5 border-t border-white/[0.03]">
                  <button className="w-full font-mono text-[0.55rem] text-accent uppercase tracking-widest flex items-center justify-center gap-3 hover:underline">
                    View Full Regional Breakdown <ArrowUpRight size={12} />
                  </button>
               </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* ATTACK TIMELINE CHART */}
            <div className="vsdp-card p-10 space-y-10 relative">
               <h3 className="font-space text-xl tracking-tight uppercase">Daily Attack Timeline</h3>
               <div className="flex items-end justify-between h-48 gap-4 px-2">
                 {attackTimeline.map((t, i) => (
                   <div key={i} className="flex-1 flex flex-col items-center gap-4 group">
                     <div className="relative w-full flex justify-center">
                       <motion.div 
                         initial={{ height: 0 }}
                         animate={{ height: `${(t.val / 600) * 100}%` }}
                         transition={{ duration: 1.5, delay: i * 0.1 }}
                         className="w-full max-w-[20px] bg-accent/20 border-t-2 border-accent group-hover:bg-accent/40 transition-colors"
                       />
                       <div className="absolute -top-8 font-mono text-[0.5rem] opacity-0 group-hover:opacity-100 transition-opacity bg-accent text-black px-1">
                         {t.val}
                       </div>
                     </div>
                     <span className="font-mono text-[0.5rem] text-muted uppercase rotate-[-45deg]">{t.label}</span>
                   </div>
                 ))}
               </div>
            </div>

            {/* PIE CHART / VECTOR SPLIT */}
            <div className="vsdp-card p-10 space-y-10">
               <h3 className="font-space text-xl tracking-tight uppercase">Attack Vector Split</h3>
               <div className="flex flex-col items-center gap-12 py-6">
                 <div className="relative w-40 h-40">
                    <svg className="w-full h-full rotate-[-90deg]">
                      <circle cx="80" cy="80" r="70" fill="none" stroke="#ff3c6e" strokeWidth="20" strokeDasharray="440" strokeDashoffset="0" />
                      <circle cx="80" cy="80" r="70" fill="none" stroke="#00e5ff" strokeWidth="20" strokeDasharray="440" strokeDashoffset="180" />
                      <circle cx="80" cy="80" r="70" fill="none" stroke="#f5c842" strokeWidth="20" strokeDasharray="440" strokeDashoffset="340" />
                    </svg>
                 </div>
                  <div className="grid grid-cols-2 gap-8 w-full">
                    <LegendItem label="Smishing" color="bg-accent" val={summary?.stats?.smishing || '0'} />
                    <LegendItem label="Vishing" color="bg-danger" val={summary?.stats?.vishing || '0'} />
                    <LegendItem label="Crypto Scam" color="bg-warning" val={summary?.stats?.crypto_scam || '0'} />
                    <LegendItem label="Firs Filed" color="bg-success" val={summary?.stats?.firs_filed || '0'} />
                  </div>
               </div>
            </div>

            {/* PERFORMANCE HUD */}
            <div className="vsdp-card p-10 space-y-10 bg-surface/50">
               <h3 className="font-space text-xl tracking-tight uppercase">System Health</h3>
               <div className="space-y-8">
                 <HealthItem label="Model Inference Speed" val="42ms" status="Optimal" />
                 <HealthItem label="API Latency" val="180ms" status="Good" />
                 <HealthItem label="DB Load" val="14%" status="Stable" />
                 <HealthItem label="Storage Utilization" val="8.2TB" status="Active" />
               </div>
               <div className="pt-8 border-t border-white/[0.03]">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded bg-accent/5 border border-accent/10 flex items-center justify-center">
                      <TrendingUp size={20} className="text-accent" />
                    </div>
                    <div className="space-y-1">
                      <div className="font-mono text-[0.6rem] text-white uppercase tracking-widest">Efficiency Up</div>
                      <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Model optimization reduced compute by 24%</div>
                    </div>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function LegendItem({ label, color, val }: any) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <div className="flex flex-col">
        <span className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">{label}</span>
        <span className="font-space text-sm font-bold">{val}</span>
      </div>
    </div>
  )
}

function HealthItem({ label, val, status }: any) {
  return (
    <div className="flex justify-between items-center">
      <div className="space-y-1">
        <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">{label}</div>
        <div className="font-space text-lg font-bold">{val}</div>
      </div>
      <div className="text-right">
        <div className="px-3 py-1 rounded-full bg-accent/5 border border-accent/20 font-mono text-[0.5rem] text-accent uppercase tracking-widest">
          {status}
        </div>
      </div>
    </div>
  )
}
