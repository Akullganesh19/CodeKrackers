'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Shield, Eye, EyeOff, Lock, Terminal, ArrowRight, User, Loader2 } from 'lucide-react'
import { setSession } from '@/backend/core/auth-utils'

export default function LoginPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMessage(null)

    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const response = await fetch('/api/v1/login/access-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setSession(data.access_token)
        router.push('/dashboard')
      } else {
        const error = await response.json()
        setErrorMessage(error.detail || "Authentication failed. Access denied.")
      }
    } catch (err) {
      setErrorMessage("Secure connection to authentication server failed.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-[#06060e] text-white selection:bg-[#7c3aed]/30 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-5%] w-[60%] h-[60%] rounded-full blur-[150px] bg-[#7c3aed]/10 opacity-40 animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[50%] h-[50%] rounded-full blur-[150px] bg-[#0aefff]/5 opacity-30" />
        <div className="absolute inset-0 bg-grid-white/[0.02]" />
      </div>

      {/* LEFT PANEL — Visual Hook */}
      <div className="hidden lg:flex w-[45%] relative flex-col justify-center items-center p-16 border-r border-white/5 z-10">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-12 max-w-sm"
        >
          <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center shadow-2xl shadow-[#7c3aed]/40 mx-auto group">
            <Shield size={44} className="text-white group-hover:scale-110 transition-transform duration-500" />
          </div>
          
          <div className="space-y-6">
            <h1 className="font-space text-5xl font-bold tracking-tighter uppercase leading-none">
              Command<br/><span className="text-[#a78bfa]">Terminal</span>
            </h1>
            <div className="h-0.5 w-12 bg-[#7c3aed] mx-auto opacity-50" />
            <p className="font-mono text-[0.65rem] text-[#64748b] uppercase tracking-[0.4em] leading-relaxed">
              Authorized personnel only. Encrypted session protocols active.
            </p>
          </div>

          <div className="flex flex-col gap-4 pt-8">
            <div className="flex items-center gap-4 text-left p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="w-2 h-2 rounded-full bg-[#0aefff] animate-ping" />
              <div className="font-mono text-[0.55rem] uppercase tracking-widest text-[#0aefff]/80">
                AES-256 Vault: ACTIVE
              </div>
            </div>
            <div className="flex items-center gap-4 text-left p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="w-2 h-2 rounded-full bg-[#7c3aed]" />
              <div className="font-mono text-[0.55rem] uppercase tracking-widest text-[#a78bfa]/80">
                RDP Protocol: SECURED
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* RIGHT PANEL — Login Form */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-20 relative z-10">
        <div className="w-full max-w-[400px] space-y-10">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7c3aed]/10 border border-[#7c3aed]/20">
              <Terminal size={12} className="text-[#a78bfa]" />
              <span className="font-mono text-[0.5rem] uppercase tracking-[0.3em] text-[#a78bfa] font-bold">Secure Gateway v2.1</span>
            </div>
            <h2 className="font-space text-3xl tracking-tighter uppercase font-bold">Personnel Authentication</h2>
          </motion.div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2 group">
              <label className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em] flex items-center gap-2 group-focus-within:text-[#a78bfa] transition-colors">
                <User size={12} /> Resource Identifier (Email)
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/[0.02] border border-white/10 px-5 py-4 rounded-xl font-mono text-sm text-white focus:border-[#7c3aed] focus:bg-white/[0.04] transition-all outline-none"
                  placeholder="name@vsdp.gov.in"
                  required
                />
              </div>
            </div>

            <div className="space-y-2 group">
              <label className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em] flex items-center gap-2 group-focus-within:text-[#a78bfa] transition-colors">
                <Lock size={12} /> Access Passphrase
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/[0.02] border border-white/10 px-5 py-4 rounded-xl font-mono text-sm text-white focus:border-[#7c3aed] focus:bg-white/[0.04] transition-all outline-none"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-[#475569] hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {errorMessage && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-mono text-[0.6rem] uppercase tracking-widest leading-relaxed"
              >
                ⚠ ALERT: {errorMessage}
              </motion.div>
            )}

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-5 rounded-xl bg-gradient-to-r from-[#7c3aed] to-[#6d28d9] hover:from-[#8b5cf6] hover:to-[#7c3aed] text-[0.65rem] font-bold uppercase tracking-[0.3em] flex items-center justify-center gap-3 shadow-xl shadow-[#7c3aed]/20 transition-all active:scale-[0.98] disabled:opacity-50"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span>Initiate Access Sequence</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="text-center pt-4">
            <span className="font-mono text-[0.55rem] text-[#64748b] uppercase tracking-[0.2em]">New Personnel? </span>
            <Link href="/register" className="font-mono text-[0.55rem] text-[#a78bfa] uppercase tracking-[0.2em] font-bold hover:underline underline-offset-4 decoration-[#7c3aed]/50">Request Clearance</Link>
          </div>
        </div>

        {/* Footer info */}
        <div className="absolute bottom-10 font-mono text-[0.45rem] text-[#475569] uppercase tracking-[0.4em] flex items-center gap-6">
          <span className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-[#0aefff] shadow-[0_0_8px_#0aefff]" />
            Encrypted
          </span>
          <span className="w-1 h-1 rounded-full bg-white/10" />
          <span>FIPS 140-2 Compliant</span>
        </div>
      </div>
    </div>
  )
}
