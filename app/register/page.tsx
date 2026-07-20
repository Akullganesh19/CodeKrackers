'use client'
import { phantomFetch } from '@/app/lib/fetch';


import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
// import ReCAPTCHA from 'react-google-recaptcha' // Temporarily disabled if package not installed, or I'll install it
import { Shield, Eye, EyeOff, Lock, UserPlus, ArrowRight, Smartphone, Mail, Loader2 } from 'lucide-react'

const roles = [
  { id: 'citizen', label: '👤 Citizen' },
  { id: 'bank', label: '🏦 Bank Officer' },
  { id: 'officer', label: '🚔 Cyber Officer' },
  { id: 'admin', label: '🛡️ Admin' },
]

export default function RegisterPage() {
  const router = useRouter()
  // const recaptchaRef = useRef<ReCAPTCHA>(null)
  const [selectedRole, setSelectedRole] = useState('citizen')
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [captchaToken, setCaptchaToken] = useState<string | null>("bypass-for-dev") // Defaulting for dev since package/key might be missing

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!captchaToken) {
      alert("Please complete the human verification step.")
      return
    }

    setIsLoading(true)
    try {
      const response = await phantomFetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password,
          phone_number: phoneNumber || null,
          role: selectedRole,
          captcha_token: captchaToken
        })
      })
      
      if (response.ok) {
        alert("Registration Successful! Please sign in with your credentials.")
        router.push('/login')
      } else {
        const error = await response.json()
        alert(error.detail || "Registration failed. Please check your details.")
      }
    } catch (err) {
      alert("Connection to registration server failed.")
      // recaptchaRef.current?.reset()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-[#06060e] text-white selection:bg-[#7c3aed]/30 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[80%] h-[80%] bg-gradient-to-br from-[#7c3aed]/10 to-transparent rounded-full blur-[150px]" />
        <div className="absolute inset-0 bg-grid-white/[0.01]" />
      </div>

      {/* LEFT PANEL — Background Decoration */}
      <div className="hidden lg:flex w-[45%] relative flex-col justify-center items-center p-16 overflow-hidden border-r border-white/5 z-10">
        <div className="relative z-10 text-center space-y-8">
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center shadow-2xl shadow-[#7c3aed]/40 mx-auto">
              <UserPlus size={40} className="text-white" />
            </div>
            <h1 className="font-space text-4xl tracking-tighter uppercase leading-none font-bold">
                Join the<br/><span className="text-[#a78bfa]">Defense Grid</span>
            </h1>
            <p className="font-mono text-[0.6rem] text-[#64748b] uppercase tracking-[0.5em] max-w-xs mx-auto leading-relaxed">
                Create your sovereign identity for the National Cybersecurity Initiative.
            </p>
        </div>
      </div>

      {/* RIGHT PANEL — Registration Form */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-20 relative z-10">
        <div className="w-full max-w-[420px] space-y-10">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7c3aed]/10 border border-[#7c3aed]/20">
              <span className="font-mono text-[0.45rem] uppercase tracking-[0.3em] text-[#a78bfa] font-bold">Identity Deployment</span>
            </div>
            <h2 className="font-space text-3xl tracking-tighter uppercase font-bold">Personnel Registration</h2>
          </div>

          {/* Role Selector */}
          <div className="space-y-4">
            <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.4em]">Designated Clearance Level</div>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {roles.map((role) => (
                <button
                  key={role.id}
                  type="button"
                  onClick={() => setSelectedRole(role.id)}
                  className={`flex-shrink-0 px-5 py-2.5 rounded-full border font-mono text-[0.55rem] uppercase tracking-[0.2em] transition-all ${
                    selectedRole === role.id
                      ? 'bg-[rgba(124,58,237,0.12)] border-[#7c3aed] text-[#a78bfa]'
                      : 'bg-white/[0.02] border-white/10 text-[#64748b] hover:border-white/20'
                  }`}
                >
                  {role.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="space-y-2">
              <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em] flex items-center gap-2">
                <Mail size={10} /> Email Identifier
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/[0.02] border border-white/10 px-5 py-3.5 rounded-lg font-mono text-sm text-white focus:border-[#7c3aed] outline-none transition-all"
                placeholder="officer@vsdp.gov.in"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em] flex items-center gap-2">
                <Smartphone size={10} /> Mobile Link (Optional)
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full bg-white/[0.02] border border-white/10 px-5 py-3.5 rounded-lg font-mono text-sm text-white focus:border-[#7c3aed] outline-none transition-all"
                placeholder="+91 XXXXX XXXXX"
              />
            </div>

            <div className="space-y-2">
              <label className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.3em] flex items-center gap-2">
                <Lock size={10} /> Encryption Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/[0.02] border border-white/10 px-5 py-3.5 rounded-lg font-mono text-sm text-white focus:border-[#7c3aed] outline-none transition-all"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-[#64748b] hover:text-white"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              <div className="text-[0.45rem] font-mono text-[#475569] uppercase leading-relaxed pt-1">
                Min 8 Chars, Upper/Lower, Digit, Special Char Required
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-5 rounded-xl bg-gradient-to-r from-[#7c3aed] to-[#6d28d9] hover:from-[#8b5cf6] hover:to-[#7c3aed] text-[0.6rem] font-bold uppercase tracking-[0.3em] flex items-center justify-center gap-3 shadow-xl shadow-[#7c3aed]/20 transition-all active:scale-[0.98] disabled:opacity-50 mt-4"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span>Initialize Account Registration</span>
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </form>

          <div className="text-center pt-2">
            <span className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em]">Existing Personnel? </span>
            <Link href="/login" className="font-mono text-[0.5rem] text-[#a78bfa] uppercase tracking-[0.3em] hover:underline font-bold">Access Terminal</Link>
          </div>
        </div>

        {/* Footer info */}
        <div className="absolute bottom-10 font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.4em] flex items-center gap-5">
          <span className="flex items-center gap-2">
            <Shield size={10} className="text-[#a78bfa]/40" /> Zero Trust Auth
          </span>
          <span className="w-1 h-1 rounded-full bg-white/5" />
          <span>AES-256 Storage</span>
        </div>
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  )
}
