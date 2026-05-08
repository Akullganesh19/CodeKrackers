'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import {
  Shield, MessageSquare, Phone, BarChart3, ArrowRight, Cpu, Lock, Globe, Zap, Scale,
  Terminal, Activity, Eye, Database, Search, LayoutGrid, ChevronDown, Sparkles,
  Radio, Siren, Network, Fingerprint, BrainCircuit, FileScan,
} from 'lucide-react'

/* ──────────────────────────────────────────────
   ANIMATED COUNTER
────────────────────────────────────────────── */
function AnimatedCounter({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })

  useEffect(() => {
    if (!isInView) return
    const duration = 2000
    const steps = 60
    const increment = value / steps
    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setCount(value)
        clearInterval(timer)
      } else {
        setCount(Math.floor(current))
      }
    }, duration / steps)
    return () => clearInterval(timer)
  }, [isInView, value])

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>
}

/* ──────────────────────────────────────────────
   SECTION HEADER
────────────────────────────────────────────── */
function SectionTag({ number, text }: { number: string; text: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      className="flex items-center gap-3 mb-8 bg-[#7c3aed]/10 w-fit px-4 py-1.5 border-l-2 border-[#7c3aed]"
    >
      <span className="font-mono text-[0.6rem] text-[#a78bfa] font-bold">{number}</span>
      <div className="h-[12px] w-[1px] bg-[#7c3aed]/30" />
      <span className="font-mono text-[0.5rem] text-[#94a3b8] uppercase tracking-[0.4em] font-bold">{text}</span>
    </motion.div>
  )
}

/* ──────────────────────────────────────────────
   FLOATING ORB DECORATION
────────────────────────────────────────────── */
function FloatingOrb({ className, color }: { className?: string; color: string }) {
  const [duration, setDuration] = useState(5)

  useEffect(() => {
    setDuration(4 + Math.random() * 3)
  }, [])

  return (
    <div className={`absolute rounded-full blur-[120px] animate-pulse ${className}`}
      style={{ background: color, animationDuration: `${duration}s` }}
    />
  )
}

/* ──────────────────────────────────────────────
   PILLAR CARD
────────────────────────────────────────────── */
function PillarCard({
  number, icon: Icon, title, color, bullets, gradient,
}: {
  number: string; icon: any; title: string; color: string; bullets: string[]; gradient: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5 }}
      className="glass-card p-8 md:p-10 relative overflow-hidden group"
    >
      {/* Gradient line top */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${gradient} opacity-60`} />

      {/* Glow on hover */}
      <div className={`absolute -inset-2 bg-gradient-to-r ${gradient} opacity-0 group-hover:opacity-[0.04] blur-3xl transition-opacity duration-700`} />

      <div className="relative z-10 space-y-6">
        <div className={`w-12 h-12 rounded-xl bg-[rgba(16,16,31,0.8)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center ${color} group-hover:scale-110 transition-transform duration-300`}>
          <Icon size={24} />
        </div>
        <h3 className={`font-space text-lg font-bold uppercase tracking-tight ${color}`}>{title}</h3>
        <ul className="space-y-3">
          {bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-3 font-mono text-[0.6rem] text-[#94a3b8]/80 leading-relaxed">
              <span className="text-[#a78bfa] mt-0.5 shrink-0">▹</span>
              {b}
            </li>
          ))}
        </ul>
      </div>

      <div className="absolute top-4 right-6 font-space text-6xl font-bold opacity-[0.03] text-white pointer-events-none select-none">
        {number}
      </div>
    </motion.div>
  )
}

/* ──────────────────────────────────────────────
   MAIN LANDING PAGE
────────────────────────────────────────────── */
export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false)
  const { scrollYProgress } = useScroll()
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0])
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 0.95])

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const stats = [
    { value: 1800000000000, label: 'Lost to cyber fraud in India annually', suffix: '', prefix: '₹' },
    { value: 74, label: 'Of scams involve voice or SMS vectors', suffix: '%', prefix: '' },
    { value: 3, label: 'Seconds to generate an AI voice clone', suffix: '', prefix: '' },
    { value: 92, label: 'Victims cannot tell AI voice from real', suffix: '%', prefix: '' },
  ]

  const architectureLayers = [
    { title: 'User Layer', items: ['React Web App', 'Mobile SDK', 'Biometric Auth', 'Real-time Alerts', 'Zero-client Audio'], gradient: 'from-[#7c3aed] to-[#a78bfa]' },
    { title: 'Zero Trust Gateway', items: ['JWT / OAuth2', 'Rate Limiter', 'SSL Pinning', 'OWASP Shield', 'IP Reputation'], gradient: 'from-[#f59e0b] to-[#fbbf24]' },
    { title: 'Detection Engine', items: ['DistilBERT (SMS)', 'Wav2Vec2 (Voice)', 'RawNet2 (Deepfake)', 'Whisper (STT)', 'GAN Artifact Scan'], gradient: 'from-[#7c3aed] to-[#0aefff]' },
    { title: 'Intelligence Layer', items: ['Scammer Profiling', 'Reputation DB', 'Honeypot Bot 🍯', 'Network Graph', 'Threat Scoring'], gradient: 'from-[#10b981] to-[#34d399]' },
    { title: 'Data & Storage', items: ['PostgreSQL', 'Redis Cache', 'Blockchain Ledger', 'AES-256 Encrypt', '90-Day Rotation'], gradient: 'from-[#64748b] to-[#94a3b8]' },
    { title: 'Compliance & Output', items: ['FIR Auto-Draft', 'cybercrime.gov.in', 'CERT-In Feed', 'Authority Portal', 'DPDP 2023'], gradient: 'from-[#ff2056] to-[#ff5777]' },
  ]

  return (
    <main className="relative min-h-screen bg-obsidian overflow-x-hidden selection:bg-[#7c3aed]/30 selection:text-white">

      {/* Grainy Texture for World-Class Feel */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#06060e] to-obsidian" />
      </div>

      {/* ═══════════════════════════════════════════
         HERO SECTION
         ═══════════════════════════════════════════ */}
      <motion.section style={{ opacity: heroOpacity, scale: heroScale }} className="relative min-h-screen flex flex-col items-center justify-center px-6 md:px-10">

        {/* Background Orbs */}
        <FloatingOrb className="top-[-10%] left-[-5%] w-[60%] h-[60%] blur-[200px] opacity-40" color="rgba(124,58,237,0.2)" />
        <FloatingOrb className="bottom-[-10%] right-[-5%] w-[50%] h-[50%]" color="rgba(10,239,255,0.06)" />
        <FloatingOrb className="top-[40%] right-[20%] w-[30%] h-[30%]" color="rgba(124,58,237,0.06)" />

        {/* NAVBAR */}
        <nav className={`fixed top-0 inset-x-0 z-[100] transition-all duration-500 border-b ${
          isScrolled
            ? 'bg-[#06060e]/90 backdrop-blur-2xl py-4 border-[rgba(124,58,237,0.1)]'
            : 'bg-transparent py-6 border-transparent'
        }`}>
          <div className="max-w-[1500px] mx-auto px-6 md:px-10 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-4 group">
            <div className="w-8 h-8 border-2 border-[#7c3aed]/40 flex items-center justify-center transition-all group-hover:border-[#7c3aed]">
              <span className="font-space font-black text-[#7c3aed] text-xs">S</span>
              </div>
            <span className="font-space font-bold text-2xl tracking-tighter text-white glow-cyber">SENTINEL</span>
            </Link>

            <div className="hidden lg:flex items-center gap-10">
              {[
                { name: 'Problem', href: '#problem' },
                { name: 'Solution', href: '#solution' },
                { name: 'Architecture', href: '#architecture' },
                { name: 'Impact', href: '#impact' },
              ].map((item) => (
                <a key={item.name} href={item.href}
                  className="font-mono text-[0.55rem] text-[#64748b] hover:text-[#a78bfa] uppercase tracking-[0.5em] transition-all duration-300 hover:drop-shadow-[0_0_12px_rgba(124,58,237,0.6)]">
                  {item.name}
                </a>
              ))}
            </div>

            <div className="flex items-center gap-6">
              <Link href="/login"
                className="font-mono text-[0.55rem] text-[#64748b] hover:text-white uppercase tracking-[0.4em] transition-colors">
                Sign In
              </Link>
              <Link href="/login" className="btn-cyber px-6 py-3 text-[0.55rem]">
                <span>Get Access</span>
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 text-center space-y-10 max-w-[1200px] px-4">
          {/* Status Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full border border-[rgba(10,239,255,0.15)] bg-[rgba(10,239,255,0.04)]"
          >
            <span className="pulse-dot neon" />
            <span className="font-mono text-[0.45rem] uppercase tracking-[0.5em] font-bold text-[#0aefff]">
              LIVE · National Cybersecurity Infrastructure · India 2026
            </span>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="font-space text-[12vw] md:text-[11vw] leading-[0.75] font-black tracking-[-0.06em] uppercase text-white"
          >
            <span className="block opacity-95">
              Cyber
            </span>
            <span className="block text-[#7c3aed] drop-shadow-[0_0_20px_rgba(124,58,237,0.4)]">
              Defense
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="font-space text-[0.9rem] md:text-[1.1rem] text-[#94a3b8] max-w-[560px] mx-auto leading-relaxed border-l-2 border-[#7c3aed]/40 pl-6 text-left"
          >
            AI-powered detection, honeypot baiting, blockchain evidence, 
            and auto-FIR filing — built for India's digital sovereignty.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-4"
          >
            <Link href="/dashboard" className="btn-cyber px-12 py-5 text-[0.6rem] flex items-center gap-3">
              <span>Enter Command Center</span>
              <ArrowRight size={16} className="group-hover:translate-x-2 transition-transform" />
            </Link>
            <button
              onClick={() => document.getElementById('architecture')?.scrollIntoView({ behavior: 'smooth' })}
              className="btn-ghost-cyber px-10 py-5 text-[0.6rem]"
            >
              View Architecture
            </button>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3"
        >
          <span className="font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.6em]">Scroll</span>
          <ChevronDown size={20} className="text-[#7c3aed]/40 animate-bounce" />
        </motion.div>
      </motion.section>

      {/* ═══════════════════════════════════════════
         DATA STREAM TICKER
         ═══════════════════════════════════════════ */}
      <div className="data-stream py-3 border-y border-[rgba(124,58,237,0.06)] bg-[#0b0b18]/50">
        <div className="data-stream-inner">
          <span className="mx-12">◈ SYS.ACTIVE — DEFENSE PROTOCOL ENGAGED — 2,607 THREATS NEUTRALIZED TODAY — 89 HONEYPOTS ACTIVE — 148 LIVE THREATS TRACKED — INFERNO MODEL v3.1 ONLINE —</span>
          <span className="mx-12">◈ SYS.ACTIVE — DEFENSE PROTOCOL ENGAGED — 2,607 THREATS NEUTRALIZED TODAY — 89 HONEYPOTS ACTIVE — 148 LIVE THREATS TRACKED — INFERNO MODEL v3.1 ONLINE —</span>
        </div>
      </div>

      {/* ═══════════════════════════════════════════
         STATS STRIP
         ═══════════════════════════════════════════ */}
      <section id="impact" className="py-20 md:py-28 px-6 md:px-10">
        <div className="max-w-[1500px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col items-center text-center gap-4 p-8 glass-card"
            >
              <span className={`font-space text-4xl md:text-5xl font-black tracking-tighter ${
                i === 0 ? 'text-[#ff2056] drop-shadow-[0_0_20px_rgba(255,32,86,0.3)]' :
                i === 1 ? 'text-[#a78bfa]' :
                i === 2 ? 'text-[#f59e0b]' :
                'text-[#10b981]'
              }`}>
                {stat.prefix}<AnimatedCounter value={stat.value} />{stat.suffix}
              </span>
              <span className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-[0.2em] max-w-[140px] leading-relaxed">
                {stat.label}
              </span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
         PROBLEM SECTION
         ═══════════════════════════════════════════ */}
      <section id="problem" className="py-28 md:py-40 px-6 md:px-10 max-w-[1400px] mx-auto space-y-16">
        <SectionTag number="01" text="The Problem" />
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="font-space text-4xl md:text-6xl font-bold tracking-tighter uppercase"
        >
          <span className="bg-gradient-to-r from-[#f5ecd7] to-[#fbbf24] bg-clip-text text-transparent">The Threat is Real</span>
        </motion.h2>

        <div className="grid md:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="glass-card p-10 md:p-14 space-y-8 relative overflow-hidden group"
          >
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-[#a78bfa] to-[#7c3aed] opacity-60" />
            <div className="text-5xl">📱</div>
            <h3 className="font-space text-2xl font-bold text-[#a78bfa] uppercase tracking-tight">Smishing</h3>
            <p className="font-mono text-[0.65rem] text-[#94a3b8]/80 leading-relaxed">
              Fraudsters send fake government SMS (e-challan, KYC alerts, bank notices) with malicious links, 
              tricking users into revealing OTPs and banking credentials. AI now personalizes messages at scale.
            </p>
            <div className="flex gap-3">
              <span className="chip chip-cyber text-[0.45rem]">AI-Personalized</span>
              <span className="chip chip-amber text-[0.45rem]">URL Spoofing</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="glass-card p-10 md:p-14 space-y-8 relative overflow-hidden group"
          >
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-[#ff2056] to-[#dc143c] opacity-60" />
            <div className="text-5xl">🎙️</div>
            <h3 className="font-space text-2xl font-bold text-[#ff2056] uppercase tracking-tight">Vishing</h3>
            <p className="font-mono text-[0.65rem] text-[#94a3b8]/80 leading-relaxed">
              AI voice cloning lets scammers impersonate police, CBI officers, or family members with 
              frightening accuracy. Victims are psychologically coerced into transferring money in real-time.
            </p>
            <div className="flex gap-3">
              <span className="chip chip-alert text-[0.45rem]">Deepfake Audio</span>
              <span className="chip chip-amber text-[0.45rem]">Real-time Cloning</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
         SIX PILLARS SECTION
         ═══════════════════════════════════════════ */}
      <section id="solution" className="py-28 md:py-40 px-6 md:px-10 max-w-[1500px] mx-auto space-y-20">
        <div className="text-center space-y-6">
          <SectionTag number="02" text="The Solution" />
          <h2 className="font-space text-4xl md:text-6xl font-bold tracking-tighter uppercase">
            <span className="bg-gradient-to-r from-white via-[#a78bfa] to-white bg-clip-text text-transparent">Six Pillars of Defense</span>
          </h2>
          <p className="font-mono text-[0.55rem] text-[#64748b] uppercase tracking-[0.4em] max-w-[600px] mx-auto">
            A multi-layered sovereign defense architecture protecting India's digital citizens
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <PillarCard
            number="01" icon={MessageSquare} title="Smishing Detection"
            color="text-[#a78bfa]" gradient="from-[#a78bfa] to-[#7c3aed]"
            bullets={[
              "DistilBERT fine-tuned on Indian scam SMS datasets",
              "Urgency keyword detection (challan, KYC, OTP expire)",
              "URL scanner with domain lookalike detection",
              "Sender ID spoofing fingerprinting",
              "Real-time warning before user clicks any link",
            ]}
          />
          <PillarCard
            number="02" icon={Phone} title="Vishing Detection"
            color="text-[#ff2056]" gradient="from-[#ff2056] to-[#dc143c]"
            bullets={[
              "RawNet2 / Wav2Vec2 for AI voice clone detection",
              "GAN artifact detection in audio streams",
              "Whisper-powered live speech-to-text transcription",
              "NLP intent scanner for OTP/money requests",
              "Real-time alert triggered within 3 seconds",
            ]}
          />
          <PillarCard
            number="03" icon={Zap} title="Honeypot & Baiting"
            color="text-[#f59e0b]" gradient="from-[#f59e0b] to-[#fbbf24]"
            bullets={[
              "AI scam-bait bot deployed when threat detected",
              "Wastes scammer's time while evidence is collected",
              "Crowdsourced blacklist — community reputation DB",
              "Voice fingerprinting across numbers",
              "One-tap auto-report to cybercrime.gov.in",
            ]}
          />
          <PillarCard
            number="04" icon={Scale} title="Legal & Compliance"
            color="text-[#a78bfa]" gradient="from-[#a78bfa] to-[#7c3aed]"
            bullets={[
              "IT Act 2000 (Sec 66C/66D) auto IPC tagging",
              "DPDP Act 2023 compliant data handling",
              "TRAI DLT framework integration",
              "Blockchain tamper-proof evidence chain",
              "FIR auto-draft with scammer details pre-filled",
            ]}
          />
          <PillarCard
            number="05" icon={Lock} title="Auth & Security"
            color="text-[#0aefff]" gradient="from-[#0aefff] to-[#06b6d4]"
            bullets={[
              "5-tier RBAC — User to Super Admin roles",
              "Zero Trust — every request re-verified",
              "On-device audio processing, data never leaves",
              "AES-256 encryption + 90-day auto expiry",
              "Root/jailbreak detection disables app",
            ]}
          />
          <PillarCard
            number="06" icon={BarChart3} title="Analytics & Intel"
            color="text-[#f59e0b]" gradient="from-[#f59e0b] to-[#fbbf24]"
            bullets={[
              "Live threat heatmap by city and district",
              "Scammer network graph — maps fraud gangs",
              "Personalized user safety score (0–100)",
              "Auto-generated national threat PDF report",
              "Model performance tracking & auto-retraining",
            ]}
          />
        </div>
      </section>

      {/* ═══════════════════════════════════════════
         ARCHITECTURE SECTION
         ═══════════════════════════════════════════ */}
      <section id="architecture" className="py-28 md:py-40 px-6 md:px-10 max-w-[1400px] mx-auto space-y-16">
        <SectionTag number="03" text="Architecture" />
        <h2 className="font-space text-4xl md:text-6xl font-bold tracking-tighter uppercase">
          <span className="bg-gradient-to-r from-white via-[#0aefff] to-white bg-clip-text text-transparent">6-Layer Defense Stack</span>
        </h2>

        <div className="space-y-3">
          {architectureLayers.map((layer, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="glass-card p-6 md:p-8 group hover:border-[rgba(124,58,237,0.2)]"
            >
              <div className="flex flex-col md:flex-row md:items-center gap-6">
                <div className="md:w-[180px] shrink-0">
                  <div className="flex items-center gap-3">
                    <div className={`w-1 h-8 rounded-full bg-gradient-to-b ${layer.gradient} opacity-60`} />
                    <span className="font-mono text-[0.55rem] text-[#94a3b8] uppercase tracking-[0.3em]">{layer.title}</span>
                  </div>
                </div>
                <div className="flex-1 flex flex-wrap gap-3">
                  {layer.items.map((item, j) => (
                    <span key={j} className="chip chip-cyber text-[0.5rem] tracking-[0.15em]">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════
         CTA SECTION
         ═══════════════════════════════════════════ */}
      <section className="py-32 md:py-40 px-6 md:px-10">
        <div className="max-w-[1400px] mx-auto relative overflow-hidden rounded-2xl border border-[rgba(124,58,237,0.1)] bg-gradient-to-br from-[rgba(124,58,237,0.05)] via-transparent to-[rgba(10,239,255,0.03)]">
          <FloatingOrb className="top-[-20%] left-[-10%] w-[50%] h-[80%]" color="rgba(124,58,237,0.08)" />
          <FloatingOrb className="bottom-[-20%] right-[-10%] w-[40%] h-[60%]" color="rgba(10,239,255,0.04)" />

          <div className="relative z-10 p-16 md:p-28 text-center space-y-12">
            <h2 className="font-space text-4xl md:text-6xl font-bold tracking-tighter uppercase">
              <span className="bg-gradient-to-r from-white via-[#a78bfa] to-white bg-clip-text text-transparent">
                Ready to defend India's<br />digital citizens?
              </span>
            </h2>
            <p className="font-mono text-[0.55rem] text-[#64748b] uppercase tracking-[0.5em]">
              Join the national cybersecurity initiative. Zero deployment cost.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <Link href="/login" className="btn-cyber px-16 py-6 text-[0.65rem]">
                <span>Access the Platform →</span>
              </Link>
              <a href="#problem" className="btn-ghost-cyber px-12 py-6 text-[0.6rem]">
                Learn How It Works
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
         FOOTER
         ═══════════════════════════════════════════ */}
      <footer className="py-24 px-6 md:px-10 border-t border-[rgba(124,58,237,0.06)]">
        <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row justify-between items-start gap-16">
          <div className="space-y-6 max-w-xs">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center">
                <span className="font-space font-black text-white text-sm">◈</span>
              </div>
              <span className="font-space font-bold text-2xl text-white">VSDP</span>
            </div>
            <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em] leading-relaxed">
              Vishing & Smishing Defense Platform — Securing the national digital identity.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-12 md:gap-20">
            {[
              { title: 'Platform', links: [{ label: 'Dashboard', href: '/dashboard' }, { label: 'SMS Scanner', href: '/sms-scanner' }, { label: 'Call Monitor', href: '/call-monitor' }] },
              { title: 'Intel', links: [{ label: 'Analytics', href: '/analytics' }, { label: 'Threat Map', href: '/analytics' }, { label: 'Reports', href: '/analytics' }] },
              { title: 'Compliance', links: [{ label: 'Legal Vault', href: '/legal' }, { label: 'Security Posture', href: '/security' }, { label: 'Certifications', href: '/tech-stack' }] },
              { title: 'Resources', links: [{ label: 'Architecture', href: '/tech-stack' }, { label: 'API Docs', href: '/docs' }, { label: 'Status', href: '/dashboard' }] },
            ].map((group) => (
              <div key={group.title} className="space-y-6">
                <h4 className="font-mono text-[0.5rem] text-[#a78bfa] uppercase tracking-[0.4em] font-bold">{group.title}</h4>
                <ul className="space-y-4">
                  {group.links.map((link) => (
                    <li key={link.label}>
                      <Link href={link.href} className="font-mono text-[0.5rem] text-[#64748b] hover:text-white uppercase tracking-[0.3em] transition-colors">
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="max-w-[1500px] mx-auto mt-20 pt-8 border-t border-[rgba(124,58,237,0.06)] flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-[0.4em]">
            © 2026 VSDP — Vishing & Smishing Defense Platform. All rights reserved.
          </div>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.3em] flex items-center gap-2">
              <Shield size={10} className="text-[#a78bfa]/40" /> AES-256
            </span>
            <span className="w-1 h-1 rounded-full bg-[rgba(124,58,237,0.2)]" />
            <span className="font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.3em]">Zero Trust</span>
            <span className="w-1 h-1 rounded-full bg-[rgba(124,58,237,0.2)]" />
            <span className="font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.3em]">CERT-In</span>
            <span className="w-1 h-1 rounded-full bg-[rgba(124,58,237,0.2)]" />
            <span className="font-mono text-[0.4rem] text-[#475569] uppercase tracking-[0.3em]">DPDP 2023</span>
          </div>
        </div>
      </footer>
    </main>
  )
}