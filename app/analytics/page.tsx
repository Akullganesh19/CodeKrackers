'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { BarChart3, Globe, TrendingUp, PieChart, Download, Calendar, Filter, ArrowUpRight, MapPin, Activity } from 'lucide-react'

export default function Analytics() {
  const heatMapData = [
    { city: 'Bengaluru', count: 1240, status: 'HIGH' },
    { city: 'Delhi', count: 980, status: 'HIGH' },
    { city: 'Mumbai', count: 850, status: 'HIGH' },
    { city: 'Hyderabad', count: 420, status: 'MEDIUM' },
    { city: 'Pune', count: 310, status: 'MEDIUM' },
    { city: 'Chennai', count: 240, status: 'LOW' },
  ]

  const attackTimeline = [
    { label: '00:00', val: 120 }, { label: '04:00', val: 40 }, { label: '08:00', val: 280 },
    { label: '12:00', val: 420 }, { label: '16:00', val: 560 }, { label: '20:00', val: 340 },
  ]

  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="Threat Intelligence Analytics" />
        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* Header */}
          <div className="flex justify-between items-end">
            <div className="space-y-3">
              <div className="section-tag">Telemetry Data</div>
              <h1 className="font-space text-4xl tracking-tighter uppercase">Threat Intel Heatmap</h1>
            </div>
            <div className="hidden md:flex gap-4">
              <button className="btn-ghost-cyber flex items-center gap-2 py-3 px-5 text-[0.5rem]"><Calendar size={13} /> Last 30 Days</button>
              <button className="btn-ghost-cyber flex items-center gap-2 py-3 px-5 text-[0.5rem]"><Filter size={13} /> Filter</button>
              <button className="btn-cyber px-6 py-3 text-[0.5rem]"><span><Download size={13} /> Export</span></button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Map */}
            <div className="lg:col-span-8 glass-card p-8 space-y-8 relative overflow-hidden">
              <div className="flex justify-between items-center">
                <h3 className="font-space text-xl tracking-tight uppercase">National Scam Distribution</h3>
                <div className="flex gap-4">
                  <span className="chip chip-alert text-[0.45rem]">High Alert</span>
                  <span className="chip chip-amber text-[0.45rem]">Medium</span>
                </div>
              </div>
              <div className="aspect-[16/9] bg-[rgba(16,16,31,0.4)] border border-[rgba(124,58,237,0.06)] rounded-lg flex items-center justify-center relative group">
                <div className="absolute inset-0 opacity-20">
                  <div className="absolute top-1/4 left-1/3 w-32 h-32 bg-[#ff2056]/30 rounded-full blur-[60px] animate-pulse" />
                  <div className="absolute bottom-1/3 right-1/4 w-40 h-40 bg-[#a78bfa]/20 rounded-full blur-[80px]" />
                </div>
                <Globe size={100} className="text-white/[0.04] group-hover:text-[#a78bfa]/10 transition-colors" />
                {['Bengaluru', 'Mumbai', 'Delhi'].map((city, i) => (
                  <div key={i} className={`absolute ${i === 0 ? 'top-1/4 left-1/3' : i === 1 ? 'bottom-1/3 right-1/4' : 'top-1/2 left-1/2'} cursor-pointer`}>
                    <span className="pulse-dot alert" />
                    <div className="bg-[rgba(11,11,24,0.9)] border border-[rgba(255,32,86,0.2)] p-2 rounded mt-2 font-mono text-[0.4rem] uppercase tracking-widest whitespace-nowrap">{city}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Cities */}
            <div className="lg:col-span-4 glass-card p-0 overflow-hidden flex flex-col">
              <div className="p-8 border-b border-[rgba(124,58,237,0.06)]">
                <h3 className="font-space text-xl tracking-tight uppercase">Top Districts</h3>
              </div>
              <div className="flex-1">
                <table className="w-full">
                  <tbody className="divide-y divide-[rgba(124,58,237,0.04)]">
                    {heatMapData.map((d, i) => (
                      <tr key={i} className="group hover:bg-[rgba(124,58,237,0.02)]">
                        <td className="px-8 py-5"><div className="flex items-center gap-4">
                          <span className="font-mono text-[0.5rem] text-[#475569]">{i + 1}</span>
                          <span className="font-mono text-[0.55rem] uppercase tracking-widest">{d.city}</span>
                        </div></td>
                        <td className="px-8 py-5 text-right">
                          <span className={`font-space font-bold ${d.status === 'HIGH' ? 'text-[#ff2056]' : d.status === 'MEDIUM' ? 'text-[#f59e0b]' : 'text-[#10b981]'}`}>
                            {d.count.toLocaleString()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass-card p-8 space-y-8">
              <h3 className="font-space text-xl tracking-tight uppercase">Daily Timeline</h3>
              <div className="flex items-end justify-between h-40 gap-3">
                {attackTimeline.map((t, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-3 group">
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${(t.val / 600) * 100}%` }}
                      transition={{ duration: 1.5, delay: i * 0.1 }}
                      className="w-full max-w-[16px] bg-[rgba(167,139,250,0.15)] border-t-2 border-[#a78bfa] group-hover:bg-[rgba(167,139,250,0.3)] transition-colors"
                    />
                    <span className="font-mono text-[0.4rem] text-[#475569] uppercase">{t.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-8 space-y-8">
              <h3 className="font-space text-xl tracking-tight uppercase">Vector Split</h3>
              <div className="flex flex-col items-center gap-8">
                <div className="relative w-36 h-36">
                  <svg className="w-full h-full rotate-[-90deg]">
                    <circle cx="72" cy="72" r="60" fill="none" stroke="#ff2056" strokeWidth="16" strokeDasharray="377" strokeDashoffset="0" />
                    <circle cx="72" cy="72" r="60" fill="none" stroke="#0aefff" strokeWidth="16" strokeDasharray="377" strokeDashoffset="155" />
                    <circle cx="72" cy="72" r="60" fill="none" stroke="#f59e0b" strokeWidth="16" strokeDasharray="377" strokeDashoffset="290" />
                  </svg>
                </div>
                <div className="grid grid-cols-2 gap-6 w-full">
                  {[
                    { label: 'Smishing', color: 'bg-[#0aefff]', val: '52%' },
                    { label: 'Vishing', color: 'bg-[#ff2056]', val: '38%' },
                    { label: 'Social Eng', color: 'bg-[#f59e0b]', val: '10%' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${item.color}`} />
                      <div>
                        <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-widest">{item.label}</div>
                        <div className="font-space text-sm font-bold">{item.val}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="glass-card p-8 space-y-8">
              <h3 className="font-space text-xl tracking-tight uppercase">System Health</h3>
              <div className="space-y-6">
                {[
                  { label: 'Model Inference', val: '42ms', status: 'Optimal' },
                  { label: 'API Latency', val: '180ms', status: 'Good' },
                  { label: 'DB Load', val: '14%', status: 'Stable' },
                  { label: 'Storage', val: '8.2TB', status: 'Active' },
                ].map((item, i) => (
                  <div key={i} className="flex justify-between items-center">
                    <div>
                      <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-widest">{item.label}</div>
                      <div className="font-space text-lg font-bold">{item.val}</div>
                    </div>
                    <span className="chip chip-neon text-[0.4rem]">{item.status}</span>
                  </div>
                ))}
              </div>
              <div className="pt-6 border-t border-[rgba(124,58,237,0.06)] flex items-center gap-4">
                <TrendingUp size={20} className="text-[#10b981]" />
                <div>
                  <div className="font-mono text-[0.5rem] text-white uppercase tracking-widest">Efficiency Up</div>
                  <div className="font-mono text-[0.4rem] text-[#64748b]">Optimization reduced compute by 24%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}