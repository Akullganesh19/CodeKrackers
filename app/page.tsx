'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Shield as LucideShield, 
  MessageSquare as LucideMessageSquare, 
  Phone as LucidePhone, 
  BarChart3 as LucideBarChart3, 
  ArrowRight as LucideArrowRight, 
  Cpu as LucideCpu, 
  Lock as LucideLock, 
  Globe as LucideGlobe, 
  Zap as LucideZap, 
  Scale as LucideScale, 
  Terminal as LucideTerminal, 
  Activity as LucideActivity, 
  Eye as LucideEye,
  Database as LucideDatabase,
  Search as LucideSearch,
  LayoutGrid as LucideLayoutGrid,
  FileText as LucideFileText
} from 'lucide-react'
import ParticleBackground from '@/components/ParticleBackground'

/* ──────────────────────────────────────────────
   HELPER COMPONENTS
────────────────────────────────────────────── */
function SectionTag({ number, text }: { number: string; text: string }) {
  return (
    <div className="flex items-center gap-4 mb-8">
      <span className="font-mono text-[0.65rem] text-accent/60 uppercase tracking-[0.4em]">{number}</span>
      <div className="h-[1px] w-8 bg-accent/20" />
      <span className="font-mono text-[0.65rem] text-muted uppercase tracking-[0.4em]">{text}</span>
    </div>
  )
}

function PillarCard({ 
  number, 
  icon: Icon, 
  title, 
  colorClass, 
  bullets,
  gesture
}: { 
  number: string; 
  icon: any; 
  title: string; 
  colorClass: string; 
  bullets: string[];
  gesture?: string;
}) {
  const handleEnter = () => {
    if (gesture) {
      window.dispatchEvent(new CustomEvent('vsdp-gesture', { detail: { type: gesture } }));
    }
  }

  const handleLeave = () => {
    window.dispatchEvent(new CustomEvent('vsdp-gesture', { detail: { type: null } }));
  }

  return (
    <div 
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      className={`relative group p-10 border-t-2 ${colorClass.replace('text', 'border')} bg-surface/30 backdrop-blur-sm overflow-hidden transition-all hover:bg-surface/50 cursor-crosshair`}
    >
      <div className="absolute top-4 right-8 font-space text-7xl font-bold opacity-[0.04] text-white pointer-events-none">{number}</div>
      <div className="relative z-10 space-y-8">
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center bg-white/[0.03] ${colorClass}`}>
          <Icon size={28} />
        </div>
        <h3 className={`font-space text-xl font-bold uppercase tracking-tight ${colorClass}`}>{title}</h3>
        <ul className="space-y-4">
          {bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-3 font-mono text-[0.7rem] text-muted/80 leading-relaxed">
              <span className="text-accent mt-0.5">→</span>
              {b}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

/* ──────────────────────────────────────────────
   MAIN LANDING PAGE
────────────────────────────────────────────── */
export default function LandingPage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    setMounted(true)
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [router])

  const stats = [
    { value: '₹1.8T', label: 'Lost to cyber fraud in India annually', color: 'text-danger' },
    { value: '74%', label: 'Of scams involve voice or SMS vectors', color: 'text-accent' },
    { value: '3 sec', label: 'To generate an AI voice clone', color: 'text-warning' },
    { value: '92%', label: 'Victims cannot tell AI voice from real', color: 'text-success' },
  ]

  const architectureLayers = [
    { title: 'User Device', items: ['React Native App', 'iOS + Android', 'Biometric Auth', 'Real-time Alerts'], color: 'bg-accent/10 text-accent border-accent/20' },
    { title: 'Zero Trust Gateway', items: ['JWT Auth', 'Rate Limiter', 'SSL Pinning', 'OWASP Shield', 'IP Whitelist'], color: 'bg-warning/10 text-warning border-warning/20' },
    { title: 'Detection Engine', items: ['BERT/DistilBERT (SMS)', 'Wav2Vec2 (Voice)', 'RawNet2 (Deepfake)', 'Whisper (STT)'], color: 'bg-accent/10 text-accent border-accent/20' },
    { title: 'Intelligence Layer', items: ['Scammer Profiling', 'Reputation DB', 'Honeypot Bot 🍯', 'Network Graph', 'Threat Scoring'], color: 'bg-surface2 text-white border-white/10' },
    { title: 'Data & Storage', items: ['PostgreSQL', 'Redis Real-time', 'Blockchain Ledger', 'AES-256 Encrypted'], color: 'bg-surface2 text-white border-white/10' },
    { title: 'Compliance & Output', items: ['FIR Auto-Draft', 'cybercrime.gov.in', 'CERT-In Feed', 'Authority Portal'], color: 'bg-danger/10 text-danger border-danger/20' },
  ]

  if (!mounted) return (
    <div className="min-h-screen bg-[#08060f] flex flex-col items-center justify-center gap-6">
      <div className="w-16 h-16 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
      <div className="font-space text-xl font-bold text-accent tracking-[0.5em] animate-pulse uppercase">VSDP_SENTINEL_LOADING</div>
    </div>
  )

  return (
    <main className="relative min-h-screen bg-transparent overflow-x-hidden selection:bg-accent/20">
      
      {/* NAVBAR */}
      <nav className={`fixed top-0 inset-x-0 z-[100] transition-all duration-500 border-b ${isScrolled ? 'bg-[#08060f]/95 backdrop-blur-xl py-4 border-accent/15' : 'bg-transparent py-8 border-transparent'}`}>
        <div className="max-w-[1500px] mx-auto px-10 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-4 group">
            <span className="font-space font-bold text-2xl tracking-tighter" style={{color:'#b197fc',textShadow:'0 0 25px rgba(177,151,252,0.6)'}}>◈ VSDP</span>
            <div className="h-4 w-[1px] bg-white/10 hidden sm:block" />
            <span className="font-mono text-[0.55rem] text-[#8892a4] uppercase tracking-[0.3em] mt-0.5 hidden sm:block">Scam Detection Platform</span>
          </Link>

          <div className="hidden lg:flex items-center gap-12">
            {[
              { name: 'SMS Scanner', href: '#sms' },
              { name: 'Call Monitor', href: '#call' },
              { name: 'Legal', href: '#legal' }
            ].map((item) => (
              <a key={item.name} href={item.href} className="font-mono text-[0.65rem] text-[#9ca3af] hover:text-[#c4b5fd] uppercase tracking-[0.4em] transition-all hover:drop-shadow-[0_0_8px_rgba(196,181,253,0.7)]">
                {item.name}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="font-mono text-[0.65rem] text-[#9ca3af] hover:text-white uppercase tracking-[0.3em] transition-colors">Dashboard</Link>
            <Link href="/dashboard" className="btn-primary px-8 py-3 text-[0.65rem] uppercase tracking-[0.3em] font-bold">
              Launch Platform
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="relative h-screen flex flex-col items-center justify-center px-10 pt-20">
        <div className="opacity-20">
          <ParticleBackground />
        </div>
        
        <div className="relative z-10 text-center space-y-12 max-w-[1200px]">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-3 px-5 py-2 rounded-sm border border-accent/30 bg-accent/[0.08] text-accent"
          >
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse inline-block" />
            <span className="font-mono text-[0.6rem] uppercase tracking-[0.4em] font-bold text-accent">Active · National Cybersecurity Infrastructure · India 2025</span>
          </motion.div>

          <h1 className="font-space text-[10vw] leading-[0.9] font-black tracking-[-0.03em] uppercase italic">
            <span className="block text-[#c4b5fd] drop-shadow-[0_0_60px_rgba(196,181,253,0.9)]">Spam</span>
            <span className="block text-[#e9d5ff] drop-shadow-[0_0_60px_rgba(233,213,255,0.8)]">Detection</span>
          </h1>

          <p className="font-space text-[1rem] text-[#9ca3af] max-w-[520px] mx-auto leading-relaxed italic border-l-2 border-[#b197fc]/30 pl-6 text-left">
            AI-powered detection, honeypot baiting, blockchain evidence, 
            and auto-FIR filing — built for India's digital future.
          </p>

          <div className="flex items-center justify-center gap-8 pt-6">
            <Link href="/dashboard" className="btn-primary px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-bold flex items-center gap-4 group">
              Explore Platform <LucideArrowRight size={16} className="group-hover:translate-x-2 transition-transform" />
            </Link>
            <button 
              onClick={() => document.getElementById('architecture')?.scrollIntoView({ behavior: 'smooth' })}
              className="btn-ghost px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-bold border-white/10 hover:border-white/20"
            >
              How It Works
            </button>
          </div>
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3">
          <span className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.5em]">Scroll</span>
          <motion.div 
            animate={{ height: [0, 40, 0], top: [0, 0, 40] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-[1px] bg-accent/40"
          />
        </div>
      </section>


      {/* SMS SCANNER SECTION */}
      <section id="sms" className="py-40 px-10 max-w-[1400px] mx-auto space-y-20">
        <SectionTag number="02" text="Smishing Defense" />
        <div className="grid lg:grid-cols-2 gap-20 items-center">
           <div className="space-y-10">
              <h2 className="font-space text-6xl font-bold text-white tracking-tighter uppercase italic">SMS Scanner</h2>
              <p className="font-space text-lg text-muted/80 leading-relaxed">
                Our BERT-powered engine analyzes incoming messages in real-time, detecting urgency patterns and suspicious URLs 
                specific to Indian regional scams (e-challan, KYC, Bank Alerts).
              </p>
              <ul className="space-y-4 font-mono text-sm text-accent">
                <li className="flex items-center gap-3">◈ Fine-tuned on 50k+ Indian scam datasets</li>
                <li className="flex items-center gap-3">◈ Real-time URL reputation scoring</li>
                <li className="flex items-center gap-3">◈ Sender ID spoofing protection</li>
              </ul>
              <Link href="/sms-scanner" className="btn-primary inline-flex px-10 py-4 text-[0.7rem] uppercase tracking-widest font-bold">
                Launch Scanner
              </Link>
           </div>
           <div className="vsdp-card p-8 bg-surface/50 border border-white/5 rounded-xl rotate-2 hover:rotate-0 transition-transform duration-700">
              <div className="p-6 bg-white/[0.03] rounded border border-white/5 space-y-4">
                 <div className="flex justify-between items-center border-b border-white/5 pb-4">
                    <span className="font-mono text-[0.6rem] text-muted">SENDER: AD-CHALLAN</span>
                    <span className="px-2 py-0.5 bg-danger/20 text-danger text-[0.5rem] font-bold rounded">THREAT DETECTED</span>
                 </div>
                 <p className="font-mono text-sm text-white/90">Your vehicle challan of Rs.500 is pending. Pay now to avoid court summons: http://bit.ly/challan-pay-ind</p>
                 <div className="pt-4 flex gap-4">
                    <div className="flex-1 h-1 bg-danger shadow-[0_0_10px_#ff3c6e]" />
                    <div className="flex-1 h-1 bg-white/10" />
                    <div className="flex-1 h-1 bg-white/10" />
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* CALL MONITOR SECTION */}
      <section id="call" className="py-40 px-10 max-w-[1400px] mx-auto space-y-20">
        <SectionTag number="03" text="Vishing Defense" />
        <div className="grid lg:grid-cols-2 gap-20 items-center">
           <div className="order-2 lg:order-1 vsdp-card p-12 bg-accent/5 border border-accent/20 rounded-full w-96 h-96 mx-auto flex items-center justify-center relative">
              <div className="absolute inset-0 border-2 border-accent/10 rounded-full animate-ping" />
              <div className="text-center space-y-4">
                 <LucidePhone size={64} className="text-accent mx-auto" />
                 <div className="font-mono text-[0.6rem] text-accent animate-pulse tracking-[0.4em]">MONITORING...</div>
              </div>
           </div>
           <div className="order-1 lg:order-2 space-y-10">
              <h2 className="font-space text-6xl font-bold text-white tracking-tighter uppercase italic">Call Monitor</h2>
              <p className="font-space text-lg text-muted/80 leading-relaxed">
                Detect AI voice clones and deepfake impersonations with RawNet2 technology. 
                VSDP provides real-time alerts within seconds of a suspicious intent detection.
              </p>
              <ul className="space-y-4 font-mono text-sm text-danger">
                <li className="flex items-center gap-3">◈ Deepfake artifact analysis (GAN detection)</li>
                <li className="flex items-center gap-3">◈ Live Neural Transcript (Whisper-STT)</li>
                <li className="flex items-center gap-3">◈ Integrated Evidence Vault</li>
              </ul>
              <Link href="/call-monitor" className="btn-ghost border-white/10 px-10 py-4 text-[0.7rem] uppercase tracking-widest font-bold">
                Open Monitor
              </Link>
           </div>
        </div>
      </section>

      {/* LEGAL & COMPLIANCE SECTION */}
      <section id="legal" className="py-40 px-10 max-w-[1400px] mx-auto space-y-20">
        <SectionTag number="04" text="Justice Tech" />
        <div className="vsdp-card p-20 bg-white/[0.01] border border-white/5 rounded-3xl text-center space-y-12">
           <h2 className="font-space text-6xl font-bold text-white tracking-tighter uppercase italic">Legal & Compliance</h2>
           <p className="font-space text-lg text-muted/80 max-w-2xl mx-auto leading-relaxed">
             Bridging the gap between detection and justice. VSDP automatically aligns every detected threat with the 
             IT Act 2000 and the DPDP Act 2023, generating court-ready evidence on the blockchain.
           </p>
           <div className="grid md:grid-cols-3 gap-8 text-left">
              <div className="p-8 bg-white/[0.02] border border-white/5 rounded-lg space-y-4">
                 <LucideFileText className="text-accent" />
                 <h4 className="font-space font-bold uppercase tracking-widest">FIR Auto-Draft</h4>
                 <p className="font-mono text-[0.6rem] text-muted uppercase">Pre-filled with scammer telemetry for cyber-cells.</p>
              </div>
              <div className="p-8 bg-white/[0.02] border border-white/5 rounded-lg space-y-4">
                 <LucideActivity className="text-success" />
                 <h4 className="font-space font-bold uppercase tracking-widest">Blockchain Ledger</h4>
                 <p className="font-mono text-[0.6rem] text-muted uppercase">Immutable chain of custody for digital evidence.</p>
              </div>
              <div className="p-8 bg-white/[0.02] border border-white/5 rounded-lg space-y-4">
                 <LucideShield className="text-warning" />
                 <h4 className="font-space font-bold uppercase tracking-widest">DPDP Compliant</h4>
                 <p className="font-mono text-[0.6rem] text-muted uppercase">Privacy-first design ensuring user data sovereignty.</p>
              </div>
           </div>
           <Link href="/legal" className="btn-primary inline-flex px-16 py-6 text-[0.8rem] uppercase tracking-widest font-bold">
             Review Legal Framework
           </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-20 px-10 border-t border-white/5 bg-[#08060f]">
        <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
          <div className="space-y-6">
            <span className="font-space font-bold text-3xl text-white tracking-tighter" style={{color:'#b197fc'}}>◈ VSDP</span>
            <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest max-w-xs leading-relaxed">
              Vishing & Smishing Defense Platform — Securing the national digital identity.
            </p>
          </div>
          <div className="flex flex-wrap gap-12 font-mono text-[0.65rem] text-muted uppercase tracking-widest">
            <Link href="/dashboard" className="hover:text-accent transition-colors">Platform</Link>
            <Link href="/tech-stack" className="hover:text-accent transition-colors">Architecture</Link>
            <Link href="/legal" className="hover:text-accent transition-colors">Legal</Link>
            <Link href="/security" className="hover:text-accent transition-colors">Security</Link>
          </div>
          <div className="font-mono text-[0.6rem] text-muted/30 uppercase tracking-[0.3em]">
            AI/ML · Security · Legal · 2025
          </div>
        </div>
      </footer>

      <style jsx global>{`
        .bg-surface {
          background-color: rgba(6, 10, 16, 0.4);
        }
        .bg-surface2 {
          background-color: rgba(255, 255, 255, 0.03);
        }
        .text-warning {
          color: #ffcc00;
        }
        .border-warning {
          border-color: #ffcc00;
        }
        .border-warning\/20 {
          border-color: rgba(255, 204, 0, 0.2);
        }
        .bg-warning\/10 {
          background-color: rgba(255, 204, 0, 0.1);
        }
      `}</style>
    </main>
  )
}
