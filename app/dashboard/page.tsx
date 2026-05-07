'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import MetricCard from '@/components/MetricCard'
import { motion } from 'framer-motion'
import {
  ShieldAlert,
  Activity,
  Zap,
  Clock,
  ArrowUpRight,
  ChevronRight,
  MessageSquare,
  Phone,
  BarChart3,
  Scale,
} from 'lucide-react'

const alerts = [
  { time: '14:32', type: 'Vishing', severity: 'HIGH', status: 'Blocked' },
  { time: '14:18', type: 'Smishing', severity: 'MEDIUM', status: 'Flagged' },
  { time: '13:55', type: 'AI Voice', severity: 'HIGH', status: 'Honeypot' },
  { time: '13:40', type: 'KYC Scam', severity: 'LOW', status: 'Warned' },
]

const quickActions = [
  { label: 'SMS Scanner', href: '/sms-scanner', icon: <MessageSquare size={18} /> },
  { label: 'Call Monitor', href: '/call-monitor', icon: <Phone size={18} /> },
  { label: 'Analytics', href: '/analytics', icon: <BarChart3 size={18} /> },
  { label: 'Legal Vault', href: '/legal', icon: <Scale size={18} /> },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

export default function Dashboard() {
  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="Command Center" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* HEADER SUMMARY */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6"
          >
            <div className="space-y-3">
              <div className="section-tag">Operational Status</div>
              <h1 className="font-space text-3xl tracking-tighter uppercase font-black">Command Center</h1>
            </div>
            <div className="status-bar">
              <span className="pulse-dot lime" />
              <span className="text-[#10b981] tracking-[0.3em] font-semibold">All Systems Nominal</span>
            </div>
          </motion.div>

          {/* ROW 1: CORE METRICS */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <motion.div variants={itemVariants}>
              <MetricCard
                label="Scams Blocked"
                value={2607}
                trend="+12%"
                isPositive={true}
                color="lime"
                icon={<ShieldAlert size={18} />}
              />
            </motion.div>
            <motion.div variants={itemVariants}>
              <MetricCard
                label="Threats Active"
                value={148}
                trend="+5%"
                isPositive={false}
                color="alert"
                icon={<Activity size={18} />}
              />
            </motion.div>
            <motion.div variants={itemVariants}>
              <MetricCard
                label="Honeypots Deployed"
                value={89}
                trend="+24%"
                isPositive={true}
                color="amber"
                icon={<Zap size={18} />}
              />
            </motion.div>
            <motion.div variants={itemVariants}>
              <MetricCard
                label="Response Latency"
                value={2.8}
                suffix="s"
                trend="-0.4s"
                isPositive={true}
                color="neon"
                icon={<Clock size={18} />}
              />
            </motion.div>
          </motion.div>

          {/* ROW 2: MAIN INTERFACE */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* SAFETY INDEX GAUGE */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="lg:col-span-4 glass-card p-10 flex flex-col items-center justify-center text-center space-y-8"
            >
              <h3 className="font-space text-lg tracking-tight uppercase font-bold">Safety Index</h3>
              <div className="relative w-56 h-56 flex items-center justify-center">
                <svg className="w-full h-full rotate-[-90deg]">
                  <circle
                    cx="112" cy="112" r="100"
                    fill="none" stroke="currentColor" strokeWidth="6"
                    className="text-white/[0.04]"
                  />
                  <motion.circle
                    cx="112" cy="112" r="100"
                    fill="none" stroke="#7c3aed" strokeWidth="6"
                    strokeDasharray="628"
                    initial={{ strokeDashoffset: 628 }}
                    animate={{ strokeDashoffset: 628 - (628 * 87) / 100 }}
                    transition={{ duration: 2.5, ease: 'circOut' }}
                    style={{ filter: 'drop-shadow(0 0 12px rgba(124,58,237,0.5))' }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-space text-7xl font-black text-white glow-cyber">87</span>
                  <span className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em] mt-2">Optimal Score</span>
                </div>
              </div>
              <div className="w-full p-5 rounded-lg bg-[rgba(16,16,31,0.4)] border border-[rgba(124,58,237,0.08)]">
                <p className="font-mono text-[0.55rem] text-[#a78bfa] uppercase tracking-[0.2em] leading-relaxed">
                  3 Threats neutralized in last 24 hours
                </p>
              </div>
            </motion.div>

            {/* LIVE INTERCEPTS */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="lg:col-span-8 glass-card p-0 overflow-hidden flex flex-col"
            >
              <div className="p-8 border-b border-[rgba(124,58,237,0.06)] flex justify-between items-center">
                <h3 className="font-space text-lg tracking-tight uppercase font-bold">Live Intercepts</h3>
                <div className="flex items-center gap-2">
                  <span className="pulse-dot alert" />
                  <span className="font-mono text-[0.45rem] text-[#ff2056] uppercase tracking-[0.3em] font-bold">Live Telemetry</span>
                </div>
              </div>
              <div className="flex-1 overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[rgba(124,58,237,0.06)] bg-[rgba(16,16,31,0.3)]">
                      <th className="px-8 py-5 text-left font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Timestamp</th>
                      <th className="px-8 py-5 text-left font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Threat Vector</th>
                      <th className="px-8 py-5 text-left font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Level</th>
                      <th className="px-8 py-5 text-right font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Protocol</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[rgba(124,58,237,0.04)]">
                    {alerts.map((alert, i) => (
                      <motion.tr
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + i * 0.1 }}
                        className="group hover:bg-[rgba(124,58,237,0.02)] transition-colors cursor-pointer"
                      >
                        <td className="px-8 py-6 font-mono text-[0.55rem] text-[#64748b]">{alert.time} UTC</td>
                        <td className="px-8 py-6 font-mono text-[0.55rem] text-white uppercase tracking-wider">{alert.type}</td>
                        <td className="px-8 py-6">
                          <span
                            className={`chip text-[0.45rem] ${
                              alert.severity === 'HIGH'
                                ? 'chip-alert'
                                : alert.severity === 'MEDIUM'
                                ? 'chip-amber'
                                : 'chip-neon'
                            }`}
                          >
                            {alert.severity}
                          </span>
                        </td>
                        <td className="px-8 py-6 text-right">
                          <div className="font-mono text-[0.5rem] text-[#64748b] group-hover:text-[#a78bfa] transition-colors flex items-center justify-end gap-2">
                            {alert.status} <ChevronRight size={12} />
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>

          {/* ROW 3: QUICK ACTIONS */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {quickActions.map((action, i) => (
              <motion.a
                key={i}
                href={action.href}
                whileHover={{ scale: 1.02 }}
                className="glass-card p-7 flex items-center justify-between group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-11 h-11 rounded-lg bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center group-hover:bg-[rgba(124,58,237,0.08)] group-hover:border-[rgba(124,58,237,0.25)] transition-all text-[#a78bfa]">
                    {action.icon}
                  </div>
                  <span className="font-mono text-[0.55rem] uppercase tracking-[0.2em] font-bold group-hover:text-white transition-colors">
                    {action.label}
                  </span>
                </div>
                <ArrowUpRight
                  size={14}
                  className="text-[#475569] group-hover:text-[#0aefff] group-hover:translate-x-1 group-hover:-translate-y-1 transition-all"
                />
              </motion.a>
            ))}
          </motion.div>
        </div>
      </main>
    </div>
  )
}