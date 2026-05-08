'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  User, Shield, Bell, Lock, Eye, 
  Database, Fingerprint, Cpu, Globe, 
  Save, AlertTriangle, Key, Smartphone,
  ChevronRight, CheckCircle2, Sliders,
  Cloud, Zap
} from 'lucide-react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'

const settingsSections = [
  { id: 'profile', icon: User, label: 'Profile', description: 'Manage your digital identity and credentials' },
  { id: 'security', icon: Shield, label: 'Security & Access', description: 'MFA, Enclave status, and session control' },
  { id: 'permissions', icon: Lock, label: 'User Permissions', description: 'RBAC level and clearance management' },
  { id: 'notifications', icon: Bell, label: 'Alert Protocols', description: 'System alerts and incident notification' },
  { id: 'enclave', icon: Cpu, label: 'TEE Configuration', description: 'Trusted Execution Environment parameters' },
  { id: 'data', icon: Database, label: 'Privacy & Data', description: 'ZK-Privacy and forensic log retention' },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = () => {
    setIsSaving(true)
    setTimeout(() => setIsSaving(false), 1500)
  }

  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary overflow-hidden">
      <Sidebar />
      
      <main className="flex-1 flex flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(124,58,237,0.05),transparent_50%)]" />
        
        <Topbar title="Operations Command" />

        <div className="flex-1 p-8 md:p-12 relative z-10 overflow-y-auto">
          <div className="max-w-6xl mx-auto space-y-12">
            
            {/* Header */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center shadow-lg shadow-[#7c3aed]/20">
                  <Sliders size={20} className="text-white" />
                </div>
                <h1 className="font-space text-4xl tracking-tighter uppercase">Operations Command</h1>
              </div>
              <p className="font-mono text-[0.6rem] text-[#64748b] uppercase tracking-[0.4em]">System Configuration // User Clearance: Level 4 Admin</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
              
              {/* Navigation Tabs */}
              <nav className="lg:col-span-4 space-y-3">
                {settingsSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveTab(section.id)}
                    className={`w-full group text-left p-4 rounded-2xl border transition-all duration-300 flex items-start gap-4 ${
                      activeTab === section.id
                        ? 'bg-[rgba(124,58,237,0.08)] border-[#7c3aed] shadow-[0_0_25px_rgba(124,58,237,0.05)]'
                        : 'bg-[rgba(16,16,31,0.4)] border-[rgba(124,58,237,0.05)] hover:border-[rgba(124,58,237,0.2)]'
                    }`}
                  >
                    <div className={`mt-1 p-2 rounded-lg transition-colors ${
                      activeTab === section.id ? 'bg-[#7c3aed] text-white' : 'bg-obsidian text-[#64748b] group-hover:text-[#a78bfa]'
                    }`}>
                      <section.icon size={18} />
                    </div>
                    <div className="flex-1">
                      <div className={`font-space text-sm tracking-tight ${activeTab === section.id ? 'text-white' : 'text-[#94a3b8]'}`}>
                        {section.label}
                      </div>
                      <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-wider mt-1">
                        {section.description}
                      </div>
                    </div>
                    <ChevronRight size={14} className={`mt-2 transition-transform ${activeTab === section.id ? 'text-[#a78bfa] translate-x-1' : 'text-transparent'}`} />
                  </button>
                ))}

                <div className="mt-8 p-6 rounded-2xl border border-[rgba(239,68,68,0.1)] bg-[rgba(239,68,68,0.03)] space-y-4">
                  <div className="flex items-center gap-2 text-red-500">
                    <AlertTriangle size={16} />
                    <span className="font-space text-xs uppercase tracking-wider">Danger Zone</span>
                  </div>
                  <button className="w-full py-3 rounded-xl border border-red-500/20 font-mono text-[0.55rem] text-red-400 uppercase tracking-widest hover:bg-red-500/10 transition-colors">
                    Nuclear Session Reset
                  </button>
                </div>
              </nav>

              {/* Content Area */}
              <div className="lg:col-span-8">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4 }}
                  className="bg-[rgba(16,16,31,0.6)] backdrop-blur-xl border border-[rgba(124,58,237,0.1)] rounded-3xl p-8 md:p-10 min-h-[600px] flex flex-col"
                >
                  <AnimatePresence mode="wait">
                    {activeTab === 'profile' && (
                      <div className="space-y-10 flex-1">
                        <div className="flex items-end gap-6">
                          <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-[#1e1e38] to-[#111126] border border-[#7c3aed]/20 flex items-center justify-center relative group">
                            <User size={40} className="text-[#a78bfa]" />
                            <div className="absolute inset-0 bg-[#7c3aed]/20 opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity flex items-center justify-center cursor-pointer">
                              <Cloud size={24} className="text-white" />
                            </div>
                          </div>
                          <div className="space-y-2">
                            <h3 className="font-space text-2xl tracking-tight text-white">Anirudh Ganesh</h3>
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                              <span className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em]">Verified Digital Asset // UID-9921</span>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-8 mt-4">
                          <div className="space-y-2">
                            <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Clearance Level</label>
                            <div className="p-4 rounded-xl bg-obsidian border border-[#7c3aed]/10 font-space text-white text-sm">
                              Level 4 - National Security
                            </div>
                          </div>
                          <div className="space-y-2">
                            <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Organization</label>
                            <div className="p-4 rounded-xl bg-obsidian border border-[#7c3aed]/10 font-space text-white text-sm">
                              Cyber Defense Command
                            </div>
                          </div>
                          <div className="space-y-2 col-span-2">
                            <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Secure Email</label>
                            <input 
                              type="text" 
                              defaultValue="anirudh.g@vsdp.gov.in"
                              className="w-full p-4 rounded-xl bg-obsidian border border-[#7c3aed]/10 font-space text-white text-sm focus:outline-none focus:border-[#7c3aed]/40 transition-colors"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {activeTab === 'security' && (
                      <div className="space-y-8 flex-1">
                        <div className="p-6 rounded-2xl bg-gradient-to-br from-[rgba(124,58,237,0.05)] to-transparent border border-[#7c3aed]/20 flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center text-[#a78bfa]">
                              <Smartphone size={24} />
                            </div>
                            <div>
                              <div className="font-space text-sm text-white">Multi-Factor Authentication</div>
                              <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-wider mt-1">Status: Active // SMS + Google Authenticator</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 text-green-400 font-mono text-[0.5rem] uppercase tracking-widest">
                            <CheckCircle2 size={10} /> Secure
                          </div>
                        </div>

                        <div className="space-y-6">
                          <div className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.4em] mb-4">Identity Verification</div>
                          <div className="flex items-center justify-between p-4 rounded-xl border border-[rgba(124,58,237,0.05)] bg-obsidian/30">
                            <div className="flex items-center gap-3">
                              <Fingerprint size={18} className="text-[#a78bfa]" />
                              <span className="font-space text-xs text-[#94a3b8]">Biometric On-Device Auth</span>
                            </div>
                            <div className="w-10 h-5 rounded-full bg-[#7c3aed]/30 relative cursor-pointer">
                              <div className="absolute right-1 top-1 w-3 h-3 rounded-full bg-[#7c3aed] shadow-[0_0_10px_rgba(124,58,237,0.8)]" />
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between p-4 rounded-xl border border-[rgba(124,58,237,0.05)] bg-obsidian/30">
                            <div className="flex items-center gap-3">
                              <Globe size={18} className="text-[#a78bfa]" />
                              <span className="font-space text-xs text-[#94a3b8]">Geo-Fenced Login Control</span>
                            </div>
                            <div className="w-10 h-5 rounded-full bg-obsidian border border-[#7c3aed]/20 relative cursor-pointer">
                              <div className="absolute left-1 top-1 w-3 h-3 rounded-full bg-[#64748b]" />
                            </div>
                          </div>
                        </div>

                        <div className="mt-auto space-y-4">
                          <div className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.4em] mb-4">TEE / Enclave Status</div>
                          <div className="flex items-center gap-4 p-4 rounded-xl bg-[rgba(124,58,237,0.02)] border border-[#7c3aed]/10">
                            <Zap size={20} className="text-[#a78bfa]" />
                            <div>
                              <div className="font-space text-[0.65rem] text-white">AMD SEV-SNP Active</div>
                              <div className="font-mono text-[0.4rem] text-[#64748b] uppercase tracking-widest mt-1">Memory Encryption Hash: 0x82...f92a</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {activeTab === 'permissions' && (
                      <div className="space-y-8 flex-1">
                        <div className="flex items-center gap-4 mb-6">
                          <Lock size={24} className="text-[#7c3aed]" />
                          <h4 className="font-space text-xl tracking-tight">Role-Based Access (RBAC)</h4>
                        </div>
                        
                        <div className="space-y-4">
                          {[
                            { name: 'Admin Dashboard', status: 'Authorized', level: 'Level 1+' },
                            { name: 'Threat Real-time Monitor', status: 'Authorized', level: 'Level 2+' },
                            { name: 'Forensic Enclave Access', status: 'Authorized', level: 'Level 4+' },
                            { name: 'Automatic FIR Authority', status: 'Restricted', level: 'Level 5 SuperAdmin' },
                            { name: 'National Node Configuration', status: 'Restricted', level: 'Level 5 SuperAdmin' },
                          ].map((perm, i) => (
                            <div key={i} className="flex items-center justify-between p-5 rounded-2xl bg-obsidian/50 border border-[rgba(124,58,237,0.05)] hover:border-[rgba(124,58,237,0.15)] transition-colors group">
                              <div className="flex items-center gap-4">
                                <div className={`w-2 h-2 rounded-full ${perm.status === 'Authorized' ? 'bg-[#7c3aed]' : 'bg-[#475569]'}`} />
                                <span className="font-space text-sm text-[#94a3b8] group-hover:text-white transition-colors">{perm.name}</span>
                              </div>
                              <div className="flex items-center gap-4">
                                <span className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-widest">{perm.level}</span>
                                <span className={`font-mono text-[0.5rem] uppercase tracking-widest px-3 py-1 rounded-full ${
                                  perm.status === 'Authorized' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                                }`}>
                                  {perm.status}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </AnimatePresence>

                  {/* Footer Action */}
                  <div className="mt-12 pt-8 border-t border-[rgba(124,58,237,0.1)] flex items-center justify-between">
                    <div className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-[0.3em]">
                      Last Update: 2024-05-08 03:36:12 UTC
                    </div>
                    <button 
                      onClick={handleSave}
                      disabled={isSaving}
                      className="btn-cyber px-8 py-3.5 flex items-center gap-3 min-w-[160px] justify-center"
                    >
                      {isSaving ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          <span className="text-[0.6rem] uppercase tracking-widest">Applying...</span>
                        </>
                      ) : (
                        <>
                          <Save size={16} />
                          <span className="text-[0.6rem] uppercase tracking-widest">Commit Changes</span>
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
