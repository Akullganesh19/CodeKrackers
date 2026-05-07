'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Shield, Check, Eye, EyeOff, Globe, Lock, Cpu, ArrowRight, Sparkles, ChevronRight } from 'lucide-react'

const roles = [
  { id: 'citizen', label: '👤 Citizen' },
  { id: 'bank', label: '🏦 Bank Officer' },
  { id: 'officer', label: '🚔 Cyber Officer' },
  { id: 'admin', label: '🛡️ Admin' },
  { id: 'superadmin', label: '⚡ Super Admin' },
]

export default function LoginPage() {
  const router = useRouter()
  const [selectedRole, setSelectedRole] = useState('citizen')
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault()
    if (email && password) {
      router.push('/dashboard')
    }
  }

  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      {/* LEFT PANEL — Brand / Info */}
      <div className="hidden lg:flex w-[45%] relative flex-col justify-between p-16 overflow-hidden">
        {/* Background orbs */}
        <div className="absolute top-[-10%] right-[-10%] w-[80%] h-[80%] bg-gradient-to-br from-[#7c3aed]/10 to-transparent rounded-full blur-[150px]" />
        <div className="absolute bottom-[-15%] left-[-15%] w-[60%] h-[60%] bg-gradient-to-tr from-[#0aefff]/05 to-transparent rounded-full blur-[120px]" />

        <div className="relative z-10 space-y-8">
          <Link href="/" className="flex items-center gap-3 group w-fit">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center shadow-lg shadow-[#7c3aed]/20 group-hover:shadow-[#7c3aed]/40 transition-all">
              <span className="font-space font-black text-white text-sm">◈</span>
            </div>
            <div>
              <span className="font-space font-bold text-xl text-white tracking-tight glow-cyber">VSDP</span>
              <span className="block font-mono text-[0.4rem] text-[#64748b] uppercase tracking-[0.4em]">Defense Command</span>
            </div>
          </Link>
        </div>

        <div className="relative z-10 space-y-16">
          <div className="space-y-6">
            <h2 className="font-space text-5xl tracking-tighter uppercase leading-[1.1]">
              <span className="bg-gradient-to-r from-white via-[#a78bfa] to-white bg-clip-text text-transparent">
                Vishing & Smishing<br />Defense Platform
              </span>
            </h2>
            <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.5em]">
              Sovereign Digital Infrastructure // India_Core
            </p>
          </div>

          {/* Animated Shield */}
          <div className="flex justify-center py-8">
            <motion.div
              animate={{ scale: [1, 1.05, 1], opacity: [0.8, 1, 0.8] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              className="w-44 h-44 rounded-full border border-[rgba(167,139,250,0.15)] flex items-center justify-center bg-[rgba(167,139,250,0.04)] shadow-[0_0_60px_rgba(124,58,237,0.1)]"
            >
              <div className="w-36 h-36 rounded-full border border-[rgba(167,139,250,0.08)] flex items-center justify-center">
                <Shield size={56} className="text-[#a78bfa]" style={{ filter: 'drop-shadow(0 0 20px rgba(167,139,250,0.4))' }} />
              </div>
            </motion.div>
          </div>

          {/* Feature List */}
          <div className="space-y-5">
            {[
              'Real-time AI threat detection',
              'Blockchain evidence chain',
              'Auto-FIR filing system',
              'Zero Trust Architecture',
              '5-Tier RBAC access control',
            ].map((text, i) => (
              <div key={i} className="flex items-center gap-4 group">
                <div className="w-5 h-5 rounded-full bg-[rgba(16,185,129,0.15)] flex items-center justify-center">
                  <Check size={12} className="text-[#10b981]" />
                </div>
                <span className="font-mono text-[0.55rem] text-[#64748b] uppercase tracking-[0.3em] group-hover:text-white transition-colors">{text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.5em]">
          ⚡ Part of India's National Cybersecurity Initiative
        </div>
      </div>

      {/* RIGHT PANEL — Login Form */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-20 relative">
        {/* Background glow */}
        <div className="absolute top-[-5%] right-[-5%] w-[50%] h-[50%] bg-gradient-to-bl from-[#7c3aed]/05 to-transparent rounded-full blur-[100px]" />

        <div className="w-full max-w-[420px] space-y-12 relative z-10">
          <div className="space-y-4">
            <div className="section-tag">Welcome Back</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">Sign in to your account</h1>
          </div>

          {/* Role Selector */}
          <div className="space-y-5">
            <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.4em]">Select Access Level</div>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {roles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => setSelectedRole(role.id)}
                  className={`flex-shrink-0 px-5 py-2.5 rounded-full border font-mono text-[0.55rem] uppercase tracking-[0.2em] transition-all ${
                    selectedRole === role.id
                      ? 'bg-[rgba(124,58,237,0.12)] border-[#7c3aed] text-[#a78bfa] shadow-[0_0_20px_rgba(124,58,237,0.1)]'
                      : 'bg-[rgba(16,16,31,0.6)] border-[rgba(124,58,237,0.1)] text-[#64748b] hover:border-[rgba(124,58,237,0.25)]'
                  }`}
                >
                  {role.label}
                </button>
              ))}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSignIn} className="space-y-6">
            <div className="space-y-2">
              <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] px-5 py-4 rounded-lg font-mono text-sm text-white focus:border-[rgba(124,58,237,0.3)] focus:outline-none focus:ring-2 focus:ring-[rgba(124,58,237,0.1)] transition-all placeholder:text-[#475569]"
                placeholder="officer@vsdp.gov.in"
                required
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em]">Password</label>
                <Link href="#" className="font-mono text-[0.45rem] text-[#a78bfa] uppercase tracking-[0.3em] hover:underline">Forgot?</Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] px-5 py-4 rounded-lg font-mono text-sm text-white focus:border-[rgba(124,58,237,0.3)] focus:outline-none focus:ring-2 focus:ring-[rgba(124,58,237,0.1)] transition-all placeholder:text-[#475569]"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-[#64748b] hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-cyber w-full py-5 text-[0.6rem] flex items-center justify-center gap-3">
              <span>Sign In</span>
              <ArrowRight size={15} />
            </button>
          </form>

          {/* Divider */}
          <div className="relative flex items-center">
            <div className="flex-grow border-t border-[rgba(124,58,237,0.08)]"></div>
            <span className="flex-shrink mx-4 font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.4em]">or continue with</span>
            <div className="flex-grow border-t border-[rgba(124,58,237,0.08)]"></div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <button className="btn-ghost-cyber flex items-center justify-center gap-3 py-4 text-[0.55rem]">
              <Globe size={14} /> Google
            </button>
            <button className="btn-ghost-cyber flex items-center justify-center gap-3 py-4 text-[0.55rem]">
              <Cpu size={14} /> Mobile OTP
            </button>
          </div>

          <div className="text-center">
            <span className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em]">Don't have an account? </span>
            <Link href="#" className="font-mono text-[0.5rem] text-[#a78bfa] uppercase tracking-[0.3em] hover:underline">Request Access</Link>
          </div>
        </div>

        <div className="absolute bottom-10 font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.4em] flex items-center gap-5">
          <span className="flex items-center gap-2">
            <Lock size={10} className="text-[#a78bfa]/40" /> AES-256
          </span>
          <span className="w-1 h-1 rounded-full bg-[rgba(124,58,237,0.15)]" />
          <span>Zero Trust</span>
          <span className="w-1 h-1 rounded-full bg-[rgba(124,58,237,0.15)]" />
          <span className="flex items-center gap-2">
            <Cpu size={10} className="text-[#a78bfa]/40" /> CERT-In
          </span>
        </div>
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  )
}