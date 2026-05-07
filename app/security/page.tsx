'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { 
  ShieldCheck, 
  Lock, 
  Key, 
  Users, 
  Fingerprint, 
  ShieldAlert, 
  RefreshCw,
  Cpu,
  ArrowRight,
  Activity
} from 'lucide-react'

export default function Security() {
  const activeSessions = [
    { user: 'BHARATH_S', role: 'Super Admin', ip: '192.168.1.104', status: 'Active', location: 'Bengaluru, IN' },
    { user: 'CYBER_OFFICER_01', role: 'L3 Officer', ip: '10.0.4.12', status: 'Active', location: 'Delhi, IN' },
    { user: 'BANK_REPR_SBI', role: 'Bank L2', ip: '45.12.8.2', status: 'Idle', location: 'Mumbai, IN' },
    { user: 'AUTO_SENTINEL', role: 'AI Bot', ip: 'Localhost', status: 'System', location: 'Core_System' },
  ]

  const rbacRoles = [
    { name: 'Citizen', access: 'L1', desc: 'Scan SMS, Report Fraud, View Safety Score' },
    { name: 'Bank Officer', access: 'L2', desc: 'View Bank-specific alerts, Mark Trusted Senders' },
    { name: 'Cyber Officer', access: 'L3', desc: 'Full Threat Intel, FIR Submission, Block Numbers' },
    { name: 'System Admin', access: 'L4', desc: 'User Management, Model Retraining, Global Settings' },
  ]

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Security & Access Control (RBAC)" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* SECURITY OVERVIEW */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
             <SecurityStat label="Authentication" val="MFA Active" sub="Biometric + OTP" icon={<Fingerprint />} />
             <SecurityStat label="Authorization" val="Zero Trust" sub="RBAC Level 3" icon={<ShieldCheck />} />
             <SecurityStat label="Encryption" val="AES-256-GCM" sub="Hardware Bound" icon={<Lock />} />
             <SecurityStat label="Integrity" val="Verified" sub="SHA-256 Chain" icon={<ShieldAlert />} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* RBAC MANAGER */}
            <div className="lg:col-span-7 vsdp-card p-10 space-y-10">
               <div className="flex justify-between items-center">
                 <h3 className="font-space text-xl tracking-tight uppercase">5-Tier RBAC Management</h3>
                 <button className="btn-ghost py-2 px-6 text-[0.6rem] uppercase tracking-widest flex items-center gap-3">
                   <Key size={14} /> Audit Permissions
                 </button>
               </div>

               <div className="grid gap-6">
                  {rbacRoles.map((role, i) => (
                    <div key={i} className="p-6 bg-surface2 border border-white/5 flex items-center justify-between group hover:border-accent/30 transition-all">
                      <div className="flex items-center gap-6">
                        <div className="w-12 h-12 rounded bg-accent/5 border border-accent/10 flex items-center justify-center font-space font-bold text-accent">
                          {role.access}
                        </div>
                        <div className="space-y-1">
                          <div className="font-mono text-[0.8rem] text-white uppercase tracking-widest">{role.name}</div>
                          <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest leading-relaxed max-w-[300px]">
                            {role.desc}
                          </div>
                        </div>
                      </div>
                      <button className="p-3 text-muted hover:text-accent transition-colors">
                        <ArrowRight size={18} />
                      </button>
                    </div>
                  ))}
               </div>
            </div>

            {/* ACTIVE SESSIONS */}
            <div className="lg:col-span-5 vsdp-card p-0 overflow-hidden flex flex-col">
               <div className="p-10 border-b border-white/[0.03] flex justify-between items-center">
                 <h3 className="font-space text-xl tracking-tight uppercase">System Sessions</h3>
                 <div className="flex items-center gap-3 px-4 py-1.5 rounded-full bg-success/5 border border-success/20">
                   <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                   <span className="font-mono text-[0.5rem] text-success uppercase tracking-[0.4em]">Live</span>
                 </div>
               </div>
               <div className="flex-1 overflow-y-auto">
                 <table className="w-full">
                    <tbody className="divide-y divide-white/[0.03]">
                      {activeSessions.map((s, i) => (
                        <tr key={i} className="group hover:bg-white/[0.01]">
                          <td className="px-10 py-6">
                            <div className="flex items-center gap-4">
                              <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_#7fff6e]" />
                              <div>
                                <div className="font-mono text-[0.7rem] text-white uppercase tracking-widest">{s.user}</div>
                                <div className="font-mono text-[0.5rem] text-muted uppercase">{s.role}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-10 py-6 text-right">
                             <div className="font-mono text-[0.6rem] text-muted">{s.ip}</div>
                             <div className="font-mono text-[0.5rem] text-accent uppercase tracking-widest">{s.location}</div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                 </table>
               </div>
               <div className="p-8 border-t border-white/[0.03] bg-white/[0.005]">
                  <button className="w-full py-4 btn-ghost text-[0.65rem] uppercase tracking-widest flex items-center justify-center gap-3">
                    <RefreshCw size={14} /> Refresh Terminal
                  </button>
               </div>
            </div>
          </div>

          {/* ZERO TRUST ARCHITECTURE MANIFESTO */}
          <div className="vsdp-card p-12 space-y-10 relative overflow-hidden bg-surface/50 border-t-4 border-t-accent">
             <div className="absolute top-0 right-0 p-12 opacity-[0.03] pointer-events-none">
               <Cpu size={240} />
             </div>
             
             <div className="space-y-4 max-w-2xl relative">
               <div className="section-tag">Sentinel Core</div>
               <h3 className="font-space text-3xl tracking-tighter uppercase">Zero Trust Security Manifest</h3>
               <p className="font-mono text-[0.65rem] text-muted uppercase tracking-widest leading-loose italic">
                 VSDP implements a "Never Trust, Always Verify" policy across all layers. 
                 Identity is confirmed through biometrics, device fingerprinting, and behavioral analysis before any data access is granted.
               </p>
             </div>

             <div className="grid md:grid-cols-3 gap-8 pt-6 relative">
               <ManifestFeature title="Identity Bound" desc="Access is tied to specific hardware and biometric signatures." />
               <ManifestFeature title="Micro-Segmentation" desc="Network segments isolated by function to prevent lateral movement." />
               <ManifestFeature title="Auto-Revoke" desc="Sessions automatically terminate on suspicious behavioral drift." />
             </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function SecurityStat({ label, val, sub, icon }: any) {
  return (
    <div className="vsdp-card p-8 space-y-4 group">
      <div className="flex justify-between items-center">
        <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">{label}</div>
        <div className="text-accent group-hover:scale-110 transition-transform">{icon}</div>
      </div>
      <div className="space-y-1">
        <div className="font-space text-xl font-bold uppercase">{val}</div>
        <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">{sub}</div>
      </div>
    </div>
  )
}

function ManifestFeature({ title, desc }: any) {
  return (
    <div className="space-y-4 p-6 border border-white/5 bg-white/[0.01]">
       <div className="flex items-center gap-4">
         <div className="w-1.5 h-1.5 rounded-full bg-accent" />
         <h4 className="font-space text-sm tracking-tight uppercase text-white">{title}</h4>
       </div>
       <p className="font-mono text-[0.55rem] text-muted uppercase tracking-widest leading-relaxed">
         {desc}
       </p>
    </div>
  )
}
