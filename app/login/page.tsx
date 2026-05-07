'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Shield, Check, Eye, EyeOff, Globe, Lock, Cpu, Phone, ArrowRight } from 'lucide-react'

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
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      {/* LEFT PANEL */}
      <div className="hidden lg:flex w-[45%] bg-surface border-r border-white/[0.03] flex-col justify-between p-20 relative overflow-hidden">
        <div className="absolute top-[-10%] right-[-10%] w-[80%] h-[80%] bg-accent/5 rounded-full blur-[120px]" />
        
        <Link href="/" className="font-space font-bold text-3xl text-accent tracking-tighter relative z-10 flex items-center gap-3">
           <div className="w-8 h-8 bg-accent/20 border border-accent/40 rotate-45 flex items-center justify-center">
             <div className="w-2 h-2 bg-accent rotate-[-45deg]" />
           </div>
           VSDP
        </Link>

        <div className="space-y-16 relative z-10">
          <div className="space-y-6">
            <h2 className="font-space text-5xl tracking-tighter uppercase leading-tight">
              Vishing & Smishing <br /> Defense Platform
            </h2>
            <p className="text-muted font-mono text-[0.6rem] uppercase tracking-[0.4em]">
              Sovereign Digital Infrastructure // India_Core
            </p>
          </div>

          <div className="flex items-center justify-center py-10">
             <motion.div 
               animate={{ scale: [1, 1.05, 1], opacity: [0.8, 1, 0.8] }}
               transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
               className="w-48 h-48 rounded-full border border-accent/20 flex items-center justify-center bg-accent/5 shadow-[0_0_60px_rgba(0,229,255,0.15)] relative"
             >
               <div className="w-40 h-40 rounded-full border border-accent/10 flex items-center justify-center">
                 <Shield size={60} className="text-accent" />
               </div>
               <div className="absolute inset-0 font-mono text-[0.4rem] text-accent/20 uppercase tracking-[2em] flex items-center justify-center rotate-animation">
                  ENCRYPTED · SECURED · SENTINEL
               </div>
             </motion.div>
          </div>

          <div className="space-y-6">
            {[
              "Real-time AI threat detection",
              "Blockchain evidence chain",
              "Auto-FIR filing system",
              "Zero Trust Architecture",
              "5-Tier RBAC access control"
            ].map((text, i) => (
              <div key={i} className="flex items-center gap-4 group">
                <div className="w-5 h-5 rounded-full bg-success/20 flex items-center justify-center">
                  <Check size={12} className="text-success" />
                </div>
                <span className="font-mono text-[0.65rem] text-muted uppercase tracking-widest group-hover:text-white transition-colors">{text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="font-mono text-[0.5rem] text-muted/40 uppercase tracking-[0.4em] relative z-10">
          Part of India's National Cybersecurity Initiative
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-20 relative">
        <div className="w-full max-w-[420px] space-y-12">
          <div className="space-y-4">
            <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.4em]">Welcome Back</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">Sign in to your account</h1>
          </div>

          {/* Role Selector */}
          <div className="space-y-6">
            <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Select Access Level</div>
            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
              {roles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => setSelectedRole(role.id)}
                  className={`flex-shrink-0 px-6 py-2 rounded-full border font-mono text-[0.65rem] uppercase tracking-widest transition-all ${
                    selectedRole === role.id 
                      ? 'bg-accent/15 border-accent text-accent shadow-[0_0_15px_rgba(0,229,255,0.1)]' 
                      : 'bg-surface2 border-white/10 text-muted hover:border-white/20'
                  }`}
                >
                  {role.label}
                </button>
              ))}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSignIn} className="space-y-8">
            <div className="space-y-3">
              <label className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-surface2 border border-white/10 px-6 py-4 rounded-md font-mono text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 transition-all"
                placeholder="officer@vsdp.gov.in"
                required
              />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <label className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Password</label>
                <Link href="#" className="font-mono text-[0.55rem] text-accent uppercase tracking-widest hover:underline">Forgot Password?</Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-surface2 border border-white/10 px-6 py-4 rounded-md font-mono text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 transition-all"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-6 top-1/2 -translate-y-1/2 text-muted hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full py-5 text-sm uppercase tracking-widest flex items-center justify-center gap-3">
              Sign In <ArrowRight size={16} />
            </button>
          </form>

          <div className="relative flex items-center py-4">
            <div className="flex-grow border-t border-white/5"></div>
            <span className="flex-shrink mx-4 font-mono text-[0.5rem] text-muted/40 uppercase tracking-widest">or continue with</span>
            <div className="flex-grow border-t border-white/5"></div>
          </div>

          <div className="grid grid-cols-2 gap-6">
             <button className="btn-ghost flex items-center justify-center gap-3 py-4 text-[0.65rem] uppercase tracking-widest">
               <Globe size={14} /> Google
             </button>
             <button className="btn-ghost flex items-center justify-center gap-3 py-4 text-[0.65rem] uppercase tracking-widest">
               <Phone size={14} /> Mobile OTP
             </button>
          </div>

          <div className="text-center">
            <span className="font-mono text-[0.65rem] text-muted uppercase tracking-widest">Don't have an account? </span>
            <Link href="#" className="font-mono text-[0.65rem] text-accent uppercase tracking-widest hover:underline">Request Access</Link>
          </div>
        </div>

        <div className="absolute bottom-12 font-mono text-[0.5rem] text-muted/40 uppercase tracking-[0.4em] flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Lock size={10} className="text-accent/40" /> AES-256 ENCRYPTED
          </div>
          <div className="w-1 h-1 rounded-full bg-white/10" />
          <div>ZERO TRUST</div>
          <div className="w-1 h-1 rounded-full bg-white/10" />
          <div className="flex items-center gap-2">
            <Cpu size={10} className="text-accent/40" /> CERT-IN COMPLIANT
          </div>
        </div>
      </div>

      <style jsx>{`
        .rotate-animation {
          animation: rotate 20s linear infinite;
        }
        @keyframes rotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  )
}

