'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import MetricCard from '@/components/MetricCard'
import { motion } from 'framer-motion'
import { 
  ShieldAlert, 
  Users, 
  Zap, 
  Clock, 
  ArrowUpRight,
  ChevronRight,
  MessageSquare,
  Phone,
  BarChart3,
  Scale
} from 'lucide-react'

export default function Dashboard() {
  const alerts = [
    { time: '14:32', type: 'Vishing', severity: 'HIGH', status: 'Blocked' },
    { time: '14:18', type: 'Smishing', severity: 'MEDIUM', status: 'Flagged' },
    { time: '13:55', type: 'AI Voice', severity: 'HIGH', status: 'Honeypot' },
    { time: '13:40', type: 'KYC Scam', severity: 'LOW', status: 'Warned' },
  ]

  return (
    <div className="flex min-h-screen bg-bg text-white">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Security HUD" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* HEADER SUMMARY */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div className="space-y-2">
              <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.4em]">Operational Status</div>
              <h1 className="font-space text-3xl tracking-tighter uppercase font-black">Platform Overview</h1>
            </div>
            <div className="px-5 py-2.5 bg-accent/5 border border-accent/20 rounded-md">
               <div className="flex items-center gap-3">
                 <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                 <span className="font-mono text-[0.6rem] text-accent uppercase tracking-widest font-bold">All Systems Nominal</span>
               </div>
            </div>
          </div>

          {/* ROW 1: CORE METRICS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <MetricCard 
              label="Scams Blocked" 
              value={2607} 
              trend="+12%" 
              isPositive={true} 
              color="success" 
              icon={<ShieldAlert size={20} />} 
            />
            <MetricCard 
              label="Threats Active" 
              value={148} 
              trend="+5%" 
              isPositive={false} 
              color="danger" 
              icon={<Users size={20} />} 
            />
            <MetricCard 
              label="Honeypots" 
              value={89} 
              trend="+24%" 
              isPositive={true} 
              color="warning" 
              icon={<Zap size={20} />} 
            />
            <MetricCard 
              label="Latency (avg)" 
              value={2.8} 
              suffix="s"
              trend="-0.4s" 
              isPositive={true} 
              color="accent" 
              icon={<Clock size={20} />} 
            />
          </div>

          {/* ROW 2: MAIN INTERFACE */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            
            {/* SAFETY HUD */}
            <div className="lg:col-span-4 vsdp-card p-12 flex flex-col items-center justify-center text-center space-y-10">
              <h3 className="font-space text-lg tracking-tight uppercase font-bold">Safety Index</h3>
              <div className="relative w-56 h-56 flex items-center justify-center">
                <svg className="w-full h-full rotate-[-90deg]">
                  <circle cx="112" cy="112" r="100" fill="none" stroke="currentColor" strokeWidth="6" className="text-white/[0.03]" />
                  <motion.circle 
                    cx="112" cy="112" r="100" fill="none" stroke="currentColor" strokeWidth="6" 
                    strokeDasharray="628"
                    initial={{ strokeDashoffset: 628 }}
                    animate={{ strokeDashoffset: 628 - (628 * 87) / 100 }}
                    transition={{ duration: 2.5, ease: "circOut" }}
                    className="text-accent"
                    style={{ filter: 'drop-shadow(0 0 10px rgba(196,181,253,0.4))' }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                   <span className="font-space text-7xl font-black text-white">87</span>
                   <span className="font-mono text-[0.6rem] text-muted uppercase tracking-widest mt-2">Optimal Score</span>
                </div>
              </div>
              <div className="space-y-4 w-full">
                <div className="p-4 bg-white/[0.02] border border-white/[0.05] rounded-md">
                   <p className="font-mono text-[0.65rem] text-accent uppercase tracking-widest leading-relaxed">
                     3 Threats neutralized <br /> in last 24 hours
                   </p>
                </div>
              </div>
            </div>

            {/* RECENT ACTIVITY */}
            <div className="lg:col-span-8 vsdp-card p-0 overflow-hidden flex flex-col">
               <div className="p-10 border-b border-white/[0.03] flex justify-between items-center">
                 <h3 className="font-space text-lg tracking-tight uppercase font-bold">Live Intercepts</h3>
                 <div className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-danger animate-pulse" />
                   <span className="font-mono text-[0.55rem] text-danger uppercase tracking-widest font-black">Live Telemetry</span>
                 </div>
               </div>
               <div className="flex-1 overflow-x-auto">
                 <table className="w-full">
                   <thead>
                     <tr className="border-b border-white/[0.03] bg-white/[0.01]">
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Timestamp</th>
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Threat Vector</th>
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Level</th>
                       <th className="px-10 py-6 text-right font-mono text-[0.55rem] text-muted uppercase tracking-widest">Protocol</th>
                     </tr>
                   </thead>
                   <tbody className="divide-y divide-white/[0.03]">
                     {alerts.map((alert, i) => (
                       <tr key={i} className="group hover:bg-white/[0.02] transition-colors">
                         <td className="px-10 py-7 font-mono text-[0.65rem] text-white/50">{alert.time} UTC</td>
                         <td className="px-10 py-7 font-mono text-[0.65rem] text-white uppercase tracking-wider">{alert.type}</td>
                         <td className="px-10 py-7">
                           <span className={`px-2.5 py-1 rounded-sm text-[0.5rem] font-black font-mono border ${
                             alert.severity === 'HIGH' ? 'bg-danger/10 text-danger border-danger/20' :
                             alert.severity === 'MEDIUM' ? 'bg-warning/10 text-warning border-warning/20' :
                             'bg-accent/10 text-accent border-accent/20'
                           }`}>
                             {alert.severity}
                           </span>
                         </td>
                         <td className="px-10 py-7 text-right">
                           <div className="font-mono text-[0.6rem] text-muted group-hover:text-accent transition-colors cursor-pointer flex items-center justify-end gap-2">
                             Details <ChevronRight size={14} />
                           </div>
                         </td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
               </div>
            </div>
          </div>

          {/* ROW 3: QUICK ACTIONS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { label: 'Scan SMS', href: '/sms-scanner', icon: <MessageSquare size={18} /> },
              { label: 'Monitor Call', href: '/call-monitor', icon: <Phone size={18} /> },
              { label: 'Analytics', href: '/analytics', icon: <BarChart3 size={18} /> },
              { label: 'Legal Vault', href: '/legal', icon: <Scale size={18} /> },
            ].map((action, i) => (
              <a key={i} href={action.href} className="vsdp-card p-8 flex items-center justify-between group hover:border-accent/40 transition-all">
                <div className="flex items-center gap-5">
                  <div className="w-12 h-12 rounded bg-white/[0.03] border border-white/5 flex items-center justify-center group-hover:bg-accent/10 group-hover:border-accent/20 transition-all">
                    {action.icon}
                  </div>
                  <span className="font-mono text-[0.7rem] uppercase tracking-[0.2em] font-bold group-hover:text-white transition-colors">{action.label}</span>
                </div>
                <ArrowUpRight size={16} className="text-muted group-hover:text-accent group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
              </a>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
