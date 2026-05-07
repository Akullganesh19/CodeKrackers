'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Shield, 
  MessageSquare, 
  Phone, 
  BarChart3, 
  ArrowRight, 
  Cpu, 
  Lock, 
  Globe, 
  Zap, 
  Scale, 
  Terminal, 
  Activity, 
  Eye,
  Database,
  Search,
  LayoutGrid,
  FileText
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
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

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
              { name: 'Problem', href: '#problem' },
              { name: 'Solution', href: '#solution' },
              { name: 'Architecture', href: '#architecture' },
              { name: 'Impact', href: '#impact' }
            ].map((item) => (
              <a key={item.name} href={item.href} className="font-mono text-[0.65rem] text-[#9ca3af] hover:text-[#c4b5fd] uppercase tracking-[0.4em] transition-all hover:drop-shadow-[0_0_8px_rgba(196,181,253,0.7)]">
                {item.name}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-8">
            <Link href="/login" className="font-mono text-[0.65rem] text-[#9ca3af] hover:text-white uppercase tracking-[0.3em] transition-colors">Login</Link>
            <Link href="/login" className="btn-primary px-8 py-3 text-[0.65rem] uppercase tracking-[0.3em] font-bold">
              Get Access
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
              Explore Platform <ArrowRight size={16} className="group-hover:translate-x-2 transition-transform" />
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

      {/* STATS STRIP */}
      <section id="impact" className="bg-[#07091a]/80 border-y border-accent/10 py-16 px-10 backdrop-blur-md">
        <div className="max-w-[1500px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-12 divide-x divide-accent/10">
          {stats.map((stat, i) => (
            <div key={i} className={`flex flex-col items-center text-center gap-3 ${i === 0 ? '' : 'pl-12'}`}>
              <span className={`font-space text-5xl font-bold tracking-tighter ${stat.color}`}>{stat.value}</span>
              <span className="font-mono text-[0.55rem] text-[#8892a4] uppercase tracking-[0.2em] max-w-[140px] leading-relaxed">
                {stat.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* PROBLEM SECTION */}
      <section id="problem" className="py-40 px-10 max-w-[1400px] mx-auto space-y-20">
        <SectionTag number="01" text="The Problem" />
        <h2 className="font-space text-5xl font-bold tracking-tighter uppercase italic" style={{color:'#f5ecd7', textShadow:'0 2px 20px rgba(201,162,39,0.2)'}}>The Threat is Real</h2>
        
        <div className="grid md:grid-cols-2 gap-10">
          <div className="p-12 border-t-2 border-accent bg-surface/30 backdrop-blur-sm space-y-8">
            <div className="text-5xl">📱</div>
            <h3 className="font-space text-2xl font-bold text-accent uppercase tracking-tight">Smishing (SMS Phishing)</h3>
            <p className="font-space text-sm text-muted/80 leading-relaxed">
              Fraudsters send fake government SMS messages (e-challan, KYC alerts, 
              bank notices) with malicious links, tricking users into revealing OTPs and 
              banking credentials. Modern smishing uses AI to personalize messages and 
              bypass spam filters.
            </p>
          </div>

          <div className="p-12 border-t-2 border-danger bg-surface/30 backdrop-blur-sm space-y-8">
            <div className="text-5xl">🎙️</div>
            <h3 className="font-space text-2xl font-bold text-danger uppercase tracking-tight">Vishing (Voice Phishing)</h3>
            <p className="font-space text-sm text-muted/80 leading-relaxed">
              AI voice cloning technology now allows scammers to impersonate police, 
              CBI officers, or even family members with frightening accuracy. Victims are 
              psychologically coerced into transferring money or revealing sensitive 
              information in real-time calls.
            </p>
          </div>
        </div>
      </section>

      {/* SIX PILLARS SECTION */}
      <section id="solution" className="py-40 px-10 max-w-[1600px] mx-auto space-y-20">
        <div className="text-center">
          <SectionTag number="02" text="The Solution" />
          <h2 className="font-space text-5xl font-bold text-white tracking-tighter uppercase italic">Six Pillars of Defense</h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <PillarCard 
            number="01"
            icon={Phone}
            title="Smishing Detection"
            colorClass="text-accent"
            gesture="left"
            bullets={[
              "BERT/DistilBERT fine-tuned on Indian scam SMS datasets",
              "Urgency keyword detection (challan, KYC, OTP expire)",
              "Suspicious URL scanner with domain lookalike detection",
              "Sender ID spoofing fingerprinting",
              "Real-time warning before user clicks any link"
            ]}
          />
          <PillarCard 
            number="02"
            icon={Activity}
            title="Vishing Detection"
            colorClass="text-danger"
            gesture="right"
            bullets={[
              "RawNet2 / Wav2Vec2 for AI voice clone detection",
              "GAN artifact detection in audio — catches deepfakes",
              "Whisper-powered live speech-to-text transcription",
              "NLP intent scanner — detects OTP/money requests mid-call",
              "Real-time alert triggered within 3 seconds"
            ]}
          />
          <PillarCard 
            number="03"
            icon={Zap}
            title="Honeypot & Baiting"
            colorClass="text-warning"
            gesture="center"
            bullets={[
              "AI scam-bait bot deployed when threat detected",
              "Wastes scammer's time while evidence is collected",
              "Crowdsourced blacklist — community-fed reputation DB",
              "Voice fingerprinting to track same scammer across numbers",
              "One-tap auto-report to cybercrime.gov.in"
            ]}
          />
          <PillarCard 
            number="04"
            icon={Scale}
            title="Legal & Compliance"
            colorClass="text-[#b06fff]"
            gesture="left"
            bullets={[
              "IT Act 2000 (Sec 66C/66D) alignment — auto IPC tagging",
              "DPDP Act 2023 compliant — consent-based data handling",
              "TRAI DLT framework integration for SMS classification",
              "Blockchain-based tamper-proof evidence chain of custody",
              "FIR auto-draft with scammer details pre-filled"
            ]}
          />
          <PillarCard 
            number="05"
            icon={Lock}
            title="Authorization & Security"
            colorClass="text-[#3b82f6]"
            gesture="right"
            bullets={[
              "5-tier RBAC — User to Super Admin roles",
              "Zero Trust Architecture — every request re-verified",
              "On-device audio processing — data never leaves phone",
              "AES-256 encryption + 90-day auto data expiry",
              "Root/jailbreak detection — app disabled on compromised devices"
            ]}
          />
          <PillarCard 
            number="06"
            icon={BarChart3}
            title="Analytics & Tracking"
            colorClass="text-[#ff8c42]"
            gesture="center"
            bullets={[
              "Live threat heatmap by city and district",
              "Scammer network graph — maps fraud gangs",
              "Personalized user safety score (gamified 0–100)",
              "Weekly auto-generated national threat PDF report",
              "Model performance tracking with auto-retraining triggers"
            ]}
          />
        </div>
      </section>

      {/* ARCHITECTURE SECTION */}
      <section id="architecture" className="py-40 px-10 max-w-[1400px] mx-auto space-y-20">
        <SectionTag number="03" text="Architecture" />
        <h2 className="font-space text-5xl font-bold text-white tracking-tighter uppercase italic">3-Layer Defense Architecture</h2>
        
        <div className="space-y-4">
          {architectureLayers.map((layer, i) => (
            <div key={i} className="flex flex-col gap-4">
              <div className="grid grid-cols-[200px_1fr] gap-10 items-center">
                <div className="text-right pr-10 border-r border-accent/30 font-mono text-[0.65rem] text-muted uppercase tracking-widest py-4">
                  {layer.title}
                </div>
                <div className="flex flex-wrap gap-4 py-4">
                  {layer.items.map((item, j) => (
                    <div key={j} className={`px-5 py-2.5 rounded border text-[0.6rem] font-mono uppercase tracking-[0.2em] font-bold ${layer.color}`}>
                      {item}
                    </div>
                  ))}
                </div>
              </div>
              {i < architectureLayers.length - 1 && (
                <div className="grid grid-cols-[200px_1fr] gap-10">
                  <div />
                  <div className="text-accent/30 pl-4 text-xl">↓</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="py-40 px-10">
        <div className="max-w-[1400px] mx-auto p-24 text-center space-y-12 bg-accent/[0.04] border-y border-white/5 rounded-3xl">
          <h2 className="font-space text-5xl font-bold text-white tracking-tighter uppercase italic">Ready to protect India's digital citizens?</h2>
          <p className="font-mono text-[0.7rem] text-muted uppercase tracking-[0.4em]">Join the national cybersecurity initiative.</p>
          <Link href="/login" className="btn-primary inline-flex px-16 py-6 text-[0.8rem] uppercase tracking-[0.4em] font-bold">
            Access the Platform →
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-20 px-10 border-t border-white/5 bg-bg">
        <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
          <div className="space-y-6">
            <span className="font-space font-bold text-3xl text-white tracking-tighter">◈ VSDP</span>
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
            AI/ML · Security · Legal · Analytics · 6 Pillars
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
