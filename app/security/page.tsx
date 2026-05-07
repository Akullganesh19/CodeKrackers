
'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Shield, Lock, Key, Users, RefreshCw, CheckCircle, XCircle, ArrowRight } from 'lucide-react'

export default function Security() {
  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="Security Posture & RBAC" />
        <div className="p-12 max-w-[1400px] mx-auto space-y-12">
          <div className="space-y-4">
            <div className="section-tag">Zero Trust Architecture</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">Security Posture</h1>
          </div>

          {/* Security Score */}
          <div className="glass-card p-10 flex flex-col lg:flex-row items-center gap-12">
            <div className="relative w-40 h-40 shrink-0">
              <svg className="w-full h-full rotate-[-90deg]">
                <circle cx="80" cy="80" r="70" fill="none" stroke="currentColor" strokeWidth="8" className="text-white/[0.04]" />
                <motion.circle cx="80" cy="80" r="70" fill="none" stroke="#10b981" strokeWidth="8"
                  strokeDasharray="440" initial={{ strokeDashoffset: 440 }}
                  animate={{ strokeDashoffset: 440 - (440 * 94) / 100 }}
                  transition={{ duration: 2, ease: 'circOut' }}
                  style={{ filter: 'drop-shadow(0 0 12px rgba(16,185,129,0.4))' }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-space text-4xl font-black text-[#10b981]">94</span>
                <span className="font-mono text-[0.4rem] text-[#64748b] uppercase tracking-widest">Score</span>
              </div>
            </div>
            <div className="flex-1 space-y-6">
              <h3 className="font-space text-2xl uppercase tracking-tight">Security Posture: <span className="text-[#10b981]">Strong</span></h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[['Encryption', 'AES-256'], ['Auth', '5-Tier RBAC'], ['Audit', 'Real-time'], ['Compliance', 'CERT-In']].map(([label, val], i) => (
                  <div key={i} className="space-y-1">
                    <div className="font-mono text-[0.4rem] text-[#64748b] uppercase tracking-widest">{label}</div>
                    <div className="font-mono text-[0.6rem] text-white">{val}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RBAC Levels */}
          <div className="glass-card p-8 space-y-8">
            <h3 className="font-space text-xl uppercase tracking-tight">Access Control Matrix</h3>
            <div className="space-y-2">
              {[
                { role: 'Citizen', level: 'L1', access: ['Report scams', 'Scan SMS', 'Monitor calls', 'View analytics'], color: 'text-[#10b981]' },
                { role: 'Bank Officer', level: 'L2', access: ['L1 + File FIRs', 'Block numbers', 'Verify senders', 'Export reports'], color: 'text-[#0aefff]' },
                { role: 'Cyber Officer', level: 'L3', access: ['L2 + Access evidence', 'Manage honeypots', 'View intelligence', 'Escalate cases'], color: 'text-[#a78bfa]' },
                { role: 'Admin', level: 'L4', access: ['L3 + User management', 'System config', 'Audit logs', 'Model training'], color: 'text-[#f59e0b]' },
                { role: 'Super Admin', level: 'L5', access: ['L4 + Full system access', 'Override controls', 'Key management', 'Infrastructure'], color: 'text-[#ff2056]' },
              ].map((rbac, i) => (
                <div key={i} className="flex items-center gap-6 p-5 rounded-lg bg-[rgba(16,16,31,0.3)] border border-[rgba(124,58,237,0.04)] hover:bg-[rgba(124,58,237,0.03)] transition-colors">
                  <div className="w-24 shrink-0">
                    <div className={`font-space text-sm uppercase tracking-tight ${rbac.color}`}>{rbac.role}</div>
                    <div className="chip chip-cyber text-[0.4rem] w-fit mt-1">{rbac.level}</div>
                  </div>
                  <div className="flex-1 flex flex-wrap gap-2">
                    {rbac.access.map((acc, j) => (
                      <span key={j} className="chip chip-neon text-[0.4rem]">{acc}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Security Features */}
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Lock, title: 'AES-256 Encryption', desc: 'All data encrypted at rest and in transit. 90-day auto-rotation policy.', color: 'text-[#0aefff]' },
              { icon: Key, title: 'Zero Trust Gateway', desc: 'Every request re-verified via JWT + OAuth2. No implicit trust.', color: 'text-[#a78bfa]' },
              { icon: RefreshCw, title: '90-Day Rotation', desc: 'Automatic key rotation, data expiry, and audit log purging.', color: 'text-[#10b981]' },
            ].map((feature, i) => (
              <div key={i} className="glass-card p-8 space-y-6 group">
                <div className={`w-12 h-12 rounded-xl bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center ${feature.color} group-hover:scale-110 transition-transform`}>
                  <feature.icon size={24} />
                </div>
                <h3 className={`font-space text-lg uppercase tracking-tight ${feature.color}`}>{feature.title}</h3>
                <p className="font-mono text-[0.5rem] text-[#64748b] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}