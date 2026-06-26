'use client'
import { dedupedFetch } from '../lib/api';


import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
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
  const [otpSent, setOtpSent] = useState(false)
  const [isSendingOtp, setIsSendingOtp] = useState(false)
  const [authMode, setAuthMode] = useState<'email' | 'otp'>('email')
  const [showGoogleModal, setShowGoogleModal] = useState(false)
  const [mobileNumber, setMobileNumber] = useState('')
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [isVerifying, setIsVerifying] = useState(false)

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    if (authMode === 'email') {
      if (email && password) {
        setIsVerifying(true)
        try {
          const res = await dedupedFetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: email,
              password: password
            })
          });
          
          if (res.ok) {
            const data = await res.json();
            localStorage.setItem('vsdp_token', data.access_token);
            localStorage.setItem('vsdp_user', JSON.stringify(data.user));
            router.push('/dashboard');
          } else {
            alert("Login failed: Invalid credentials");
          }
        } catch (err) {
          console.error("Auth error", err);
          alert("Connection error to security gateway");
        } finally {
          setIsVerifying(false);
        }
      }
    } else {
      // Mock OTP flow (requires real SMS gateway)
      if (otpSent) {
        if (otp.every(d => d !== '')) {
          setIsVerifying(true)
          setTimeout(() => router.push('/dashboard'), 1500)
        }
      } else {
        if (mobileNumber.length === 10) {
          setIsSendingOtp(true)
          setTimeout(() => {
            setIsSendingOtp(false)
            setOtpSent(true)
          }, 1500)
        }
      }
    }
  }

  const handleGoogleLogin = () => {
    setShowGoogleModal(true)
  }

  const selectGoogleAccount = (acc: string) => {
    setShowGoogleModal(false)
    setIsVerifying(true)
    setTimeout(() => router.push('/dashboard'), 1500)
  }

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      {/* Google Modal Overlay */}
      <AnimatePresence>
        {showGoogleModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-[#1a1c2e] border border-white/10 p-10 rounded-2xl w-full max-w-[400px] space-y-8"
            >
              <div className="text-center space-y-2">
                <Globe size={48} className="mx-auto text-accent mb-4" />
                <h3 className="font-space text-2xl font-bold uppercase tracking-tight">Choose an account</h3>
                <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">to continue to VSDP Gateway</p>
              </div>

              <div className="space-y-3">
                {[
                  { name: 'Cyber Officer', email: 'officer.krishna@gov.in', img: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Krishna' },
                  { name: 'Admin Account', email: 'admin.sharma@vsdp.org', img: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sharma' },
                  { name: 'Citizen Access', email: 'bharat.user@gmail.com', img: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bharat' }
                ].map((acc) => (
                  <button 
                    key={acc.email}
                    onClick={() => selectGoogleAccount(acc.email)}
                    className="w-full flex items-center gap-4 p-4 bg-white/[0.02] border border-white/5 rounded-xl hover:bg-white/[0.05] hover:border-accent/30 transition-all group"
                  >
                    <img src={acc.img} className="w-10 h-10 rounded-full bg-white/10" alt="" />
                    <div className="text-left">
                      <div className="font-mono text-sm font-bold text-white group-hover:text-accent">{acc.name}</div>
                      <div className="font-mono text-[0.6rem] text-muted uppercase">{acc.email}</div>
                    </div>
                  </button>
                ))}
              </div>

              <button 
                onClick={() => setShowGoogleModal(false)}
                className="w-full py-4 font-mono text-[0.6rem] text-muted uppercase tracking-widest hover:text-white transition-colors"
              >
                Cancel
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Overlay */}
      <AnimatePresence>
        {(isVerifying || isSendingOtp) && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[300] bg-bg flex flex-col items-center justify-center space-y-8"
          >
            <div className="w-24 h-24 rounded-full border-2 border-accent/20 border-t-accent animate-spin" />
            <div className="text-center space-y-2">
              <div className="font-space text-2xl font-bold uppercase tracking-widest text-accent animate-pulse">
                {isSendingOtp ? 'Transmitting Code' : 'Establishing Session'}
              </div>
              <div className="font-mono text-[0.6rem] text-muted uppercase tracking-[0.4em]">
                {isSendingOtp ? 'Securing GSM Gateway...' : 'Zero Trust Handshake in Progress...'}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

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
            <h1 className="font-space text-4xl tracking-tighter uppercase">{authMode === 'email' ? 'Sign in to account' : otpSent ? 'Verification Required' : 'Mobile Gateway'}</h1>
          </div>

          {/* Role Selector */}
          {!otpSent && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Select Access Level</div>
              <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    suppressHydrationWarning={true}
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
          )}

          {/* Form */}
          <form onSubmit={handleSignIn} className="space-y-8">
            {authMode === 'email' ? (
              <>
                <div className="space-y-3">
                  <label className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    suppressHydrationWarning={true}
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
                      suppressHydrationWarning={true}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-surface2 border border-white/10 px-6 py-4 rounded-md font-mono text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 transition-all"
                      placeholder="••••••••"
                      required
                    />
                    <button
                      type="button"
                      suppressHydrationWarning={true}
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-6 top-1/2 -translate-y-1/2 text-muted hover:text-white transition-colors"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {!otpSent ? (
                  <div className="space-y-3">
                    <label className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Mobile Number</label>
                    <div className="relative">
                      <span className="absolute left-6 top-1/2 -translate-y-1/2 font-mono text-sm text-accent">+91</span>
                      <input
                        type="tel"
                        value={mobileNumber}
                        onChange={(e) => setMobileNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                        className="w-full bg-surface2 border border-white/10 pl-16 pr-6 py-4 rounded-md font-mono text-sm focus:border-accent focus:outline-none transition-all"
                        placeholder="9876543210"
                        required
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6 animate-in zoom-in-95 duration-500">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Enter Code Sent to</div>
                        <div className="font-mono text-sm text-white">+91 {mobileNumber}</div>
                      </div>
                      <button 
                        type="button"
                        onClick={() => setOtpSent(false)}
                        className="font-mono text-[0.5rem] text-accent uppercase tracking-widest hover:underline"
                      >
                        Change Number
                      </button>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <label className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">6-Digit Verification Code</label>
                        <button type="button" className="font-mono text-[0.5rem] text-accent uppercase tracking-widest hover:underline">Resend OTP</button>
                      </div>
                      <div className="flex justify-between gap-2">
                        {otp.map((digit, i) => (
                          <input
                            key={i}
                            type="text"
                            maxLength={1}
                            value={digit}
                            onChange={(e) => {
                              const val = e.target.value.slice(-1)
                              if (/^\d*$/.test(val)) {
                                const newOtp = [...otp]
                                newOtp[i] = val
                                setOtp(newOtp)
                                if (val && i < 5) {
                                  const nextInput = e.currentTarget.parentElement?.children[i + 1] as HTMLInputElement
                                  if (nextInput) nextInput.focus()
                                }
                              }
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Backspace' && !otp[i] && i > 0) {
                                const prevInput = e.currentTarget.parentElement?.children[i - 1] as HTMLInputElement
                                if (prevInput) prevInput.focus()
                              }
                            }}
                            className="w-12 h-14 bg-surface2 border border-white/10 text-center font-space text-xl font-bold rounded-md focus:border-accent focus:outline-none transition-all"
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            <button type="submit" suppressHydrationWarning={true} className="btn-primary w-full py-5 text-sm uppercase tracking-widest flex items-center justify-center gap-3">
              {authMode === 'email' ? 'Secure Sign In' : otpSent ? 'Verify & Continue' : 'Send Verification OTP'} <ArrowRight size={16} />
            </button>
            
            {(authMode === 'otp' || otpSent) && (
              <button 
                type="button" 
                onClick={() => {
                  setAuthMode('email')
                  setOtpSent(false)
                }}
                className="w-full py-2 font-mono text-[0.5rem] text-muted uppercase tracking-widest hover:text-white transition-colors"
              >
                ← Back to Email Sign In
              </button>
            )}
          </form>

          <div className="relative flex items-center py-4">
            <div className="flex-grow border-t border-white/5"></div>
            <span className="flex-shrink mx-4 font-mono text-[0.5rem] text-muted/40 uppercase tracking-widest">or continue with</span>
            <div className="flex-grow border-t border-white/5"></div>
          </div>

          <div className="grid grid-cols-2 gap-6">
             <button 
              onClick={handleGoogleLogin}
              className="btn-ghost flex items-center justify-center gap-3 py-4 text-[0.65rem] uppercase tracking-widest group"
             >
               <Globe size={14} className="group-hover:text-accent transition-colors" /> Google
             </button>
             <button 
              onClick={() => setAuthMode(authMode === 'email' ? 'otp' : 'email')}
              className={`btn-ghost flex items-center justify-center gap-3 py-4 text-[0.65rem] uppercase tracking-widest transition-all ${authMode === 'otp' ? 'border-accent text-accent' : ''}`}
             >
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

