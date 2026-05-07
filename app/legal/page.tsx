'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Scale, FileText, Shield, BookOpen, Gavel, CheckCircle, ArrowRight } from 'lucide-react'

export default function Legal() {
  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="Legal & Compliance Vault" />
        <div className="p-12 max-w-[1400px] mx-auto space-y-12">
          <div className="space-y-4">
            <div className="section-tag">Regulatory Framework</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">Legal & Compliance Vault</h1>
            <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.4em]">
              IT Act 2000 · DPDP Act 2023 · TRAI DLT · CERT-In Compliant
            </p>
          </div>

          {/* Compliance Badges */}
          <div className="flex flex-wrap gap-4">
            {['IT Act Sec 66C/66D', 'DPDP Act 2023', 'TRAI DLT', 'CERT-In', 'IPC Auto-Tagging', 'Blockchain Evidence'].map((badge, i) => (
              <span key={i} className="chip chip-cyber text-[0.5rem]">{badge}</span>
            ))}
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* FIR Auto-Draft */}
            <div className="glass-card p-8 space-y-8 col-span-2">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-[rgba(255,32,86,0.1)] border border-[rgba(255,32,86,0.15)] flex items-center justify-center text-[#ff2056]">
                  <FileText size={24} />
                </div>
                <div>
                  <h3 className="font-space text-xl uppercase tracking-tight">FIR Auto-Draft System</h3>
                  <p className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-widest">Pre-filled with scammer details</p>
                </div>
              </div>
              <div className="bg-[rgba(16,16,31,0.4)] border border-[rgba(124,58,237,0.06)] rounded-lg p-6 font-mono text-[0.5rem] text-[#94a3b8] leading-relaxed space-y-2">
                <p className="text-[#a78bfa]">// Generated FIR Draft — Case #VSDP-2026-04-1423</p>
                <p>To: The Station House Officer, Cyber Crime Police Station</p>
                <p>Subject: Complaint regarding AI-assisted vishing fraud</p>
                <p>---</p>
                <p>I, [Citizen Name], hereby lodge this complaint against unknown</p>
                <p>person(s) who contacted me via phone call at [Timestamp]...</p>
              </div>
              <button className="btn-cyber w-fit px-8 py-4 text-[0.5rem]"><span>Generate New Draft →</span></button>
            </div>

            {/* Key Stats */}
            <div className="glass-card p-8 space-y-8">
              <h3 className="font-space text-xl uppercase tracking-tight">Compliance Stats</h3>
              <div className="space-y-8">
                {[
                  { label: 'FIRs Filed', val: '1,247', color: 'text-[#ff2056]' },
                  { label: 'Evidence Chains', val: '3,892', color: 'text-[#a78bfa]' },
                  { label: 'Blockchain Anchors', val: '8,401', color: 'text-[#0aefff]' },
                  { label: 'Active Investigations', val: '156', color: 'text-[#f59e0b]' },
                ].map((stat, i) => (
                  <div key={i} className="flex justify-between items-center pb-4 border-b border-[rgba(124,58,237,0.04)] last:border-0">
                    <span className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-widest">{stat.label}</span>
                    <span className={`font-space text-2xl font-black ${stat.color}`}>{stat.val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Legal Frameworks */}
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Gavel, title: 'IT Act 2000', items: ['Sec 66C — Identity Theft', 'Sec 66D — Cheating by Impersonation', 'IPC 420 — Cheating & Dishonesty', 'IPC 468 — Forgery for Cheating'], color: 'text-[#a78bfa]' },
              { icon: Shield, title: 'DPDP Act 2023', items: ['Consent-based Data Processing', '90-Day Auto Data Expiry', 'Right to Erasure Compliant', 'Data Protection Officer Interface'], color: 'text-[#0aefff]' },
              { icon: BookOpen, title: 'TRAI DLT Framework', items: ['SMS Header Registration', 'Content Template Registry', 'Sender ID Verification', 'Spam Threshold Monitoring'], color: 'text-[#10b981]' },
            ].map((framework, i) => (
              <div key={i} className="glass-card p-8 space-y-6 group">
                <div className={`w-12 h-12 rounded-xl bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center ${framework.color} group-hover:scale-110 transition-transform`}>
                  <framework.icon size={24} />
                </div>
                <h3 className={`font-space text-lg uppercase tracking-tight ${framework.color}`}>{framework.title}</h3>
                <ul className="space-y-3">
                  {framework.items.map((item, j) => (
                    <li key={j} className="flex items-start gap-3 font-mono text-[0.5rem] text-[#94a3b8]">
                      <span className="text-[#a78bfa] mt-0.5">▹</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}