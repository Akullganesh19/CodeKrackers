'use client'

import { useRef, useState, useEffect, Suspense, lazy } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const RobotScene = lazy(() => import('@/components/RobotScene'))

/* ─── FEATURE HOTSPOTS ───────────────────────────────────────────── */
const HOTSPOTS = [
  {
    id: 'sms',
    x: '14%', y: '35%',
    label: 'SMS Intelligence',
    desc: 'BERT-powered classification detects smishing with 95%+ accuracy across all Indian dialects and scam patterns in real-time.',
    accent: '#00e5ff',
  },
  {
    id: 'voice',
    x: '76%', y: '30%',
    label: 'Voice Deepfake AI',
    desc: 'RawNet2 & Wav2Vec2 models analyze live audio streams to detect AI-synthesized voices and spoofed caller identities.',
    accent: '#7fff6e',
  },
  {
    id: 'blockchain',
    x: '12%', y: '65%',
    label: 'Blockchain Evidence',
    desc: 'Hyperledger Fabric creates immutable, timestamped evidence packages — court-admissible and tamper-proof by design.',
    accent: '#f5c842',
  },
  {
    id: 'honeypot',
    x: '74%', y: '62%',
    label: 'Honeypot System',
    desc: 'Active-defense decoy network lures scammers into controlled environments, harvesting intelligence on attack vectors.',
    accent: '#ff3c6e',
  },
]

/* ─── FLOATING CARD ──────────────────────────────────────────────── */
function FeatureCard({ hotspot }: { hotspot: typeof HOTSPOTS[0] }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.88, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.88, y: 10 }}
      transition={{ type: 'spring', stiffness: 260, damping: 22 }}
      className="absolute z-30 w-[260px] pointer-events-none"
      style={{
        left: hotspot.x,
        top: hotspot.y,
        transform: 'translate(-50%, -110%)',
      }}
    >
      <div
        className="rounded-xl p-5 backdrop-blur-xl border"
        style={{
          background: 'rgba(6,10,16,0.82)',
          borderColor: hotspot.accent + '40',
          boxShadow: `0 0 30px ${hotspot.accent}18, 0 8px 32px rgba(0,0,0,0.6)`,
        }}
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: hotspot.accent, boxShadow: `0 0 8px ${hotspot.accent}` }} />
          <span className="font-mono text-[0.65rem] uppercase tracking-[0.25em]" style={{ color: hotspot.accent }}>
            {hotspot.label}
          </span>
        </div>
        <p className="text-[0.78rem] text-[#8fa0b8] leading-relaxed">{hotspot.desc}</p>
      </div>
      {/* Arrow */}
      <div className="flex justify-center">
        <div className="w-px h-6" style={{ background: `linear-gradient(to bottom, ${hotspot.accent}80, transparent)` }} />
      </div>
    </motion.div>
  )
}

/* ─── HOTSPOT DOT ────────────────────────────────────────────────── */
function HotspotDot({ hotspot, onEnter, onLeave }: { hotspot: typeof HOTSPOTS[0]; onEnter: () => void; onLeave: () => void }) {
  return (
    <div
      className="absolute z-20 cursor-crosshair"
      style={{ left: hotspot.x, top: hotspot.y, transform: 'translate(-50%, -50%)' }}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
    >
      {/* Outer ping ring */}
      <div
        className="absolute inset-0 rounded-full animate-ping opacity-40"
        style={{ width: 40, height: 40, margin: -12, background: hotspot.accent + '30', border: `1px solid ${hotspot.accent}50` }}
      />
      {/* Dot */}
      <div
        className="w-3 h-3 rounded-full border-2 transition-all duration-300 hover:scale-150"
        style={{ borderColor: hotspot.accent, background: hotspot.accent + '40', boxShadow: `0 0 12px ${hotspot.accent}80` }}
      />
    </div>
  )
}

/* ─── SCAN LINE OVERLAY ──────────────────────────────────────────── */
function ScanBar() {
  return (
    <motion.div
      className="absolute left-0 right-0 h-px pointer-events-none z-10"
      style={{ background: 'linear-gradient(90deg, transparent, #00e5ff40, #00e5ff80, #00e5ff40, transparent)' }}
      animate={{ top: ['0%', '100%'] }}
      transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
    />
  )
}

/* ─── BOTTOM HUD BAR ─────────────────────────────────────────────── */
function HUDBar() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const update = () => setTime(new Date().toLocaleTimeString('en-IN', { hour12: false }))
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="absolute bottom-0 left-0 right-0 z-20 flex items-center justify-between px-10 py-4 border-t border-[rgba(0,229,255,0.08)]"
      style={{ background: 'linear-gradient(to top, rgba(6,10,16,0.9), transparent)' }}>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-[#7fff6e] animate-pulse shadow-[0_0_6px_#7fff6e]" />
          <span className="font-mono text-[0.6rem] text-[#7fff6e] uppercase tracking-widest">Systems Online</span>
        </div>
        <span className="font-mono text-[0.6rem] text-[#3a4a60] uppercase tracking-widest">VSDP • AI Core v4.2.1</span>
      </div>
      <span className="font-mono text-[0.6rem] text-[#3a4a60] uppercase tracking-widest tabular-nums">{time}</span>
    </div>
  )
}

/* ─── MAIN PAGE ──────────────────────────────────────────────────── */
export default function RobotLandingPage() {
  const cursorRef = useRef({ x: 0, y: 0 })
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setTimeout(() => setMounted(true), 0)
    const handleMove = (e: MouseEvent) => {
      cursorRef.current.x = (e.clientX / window.innerWidth - 0.5) * 2
      cursorRef.current.y = (e.clientY / window.innerHeight - 0.5) * 2
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  const activeHotspotData = HOTSPOTS.find(h => h.id === activeHotspot)

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#060a10] select-none">
      {/* Deep radial background gradient */}
      <div className="absolute inset-0 z-0"
        style={{ background: 'radial-gradient(ellipse 80% 80% at 50% 50%, #0a1628 0%, #060a10 70%)' }}
      />

      {/* Grid overlay */}
      <div className="absolute inset-0 z-0"
        style={{
          backgroundImage: 'linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px)',
          backgroundSize: '60px 60px'
        }}
      />

      {/* Scanline overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none"
        style={{
          background: 'repeating-linear-gradient(rgba(0,0,0,0.03) 0px, rgba(0,0,0,0.03) 1px, transparent 1px, transparent 4px)'
        }}
      />

      {/* Vignette */}
      <div className="absolute inset-0 z-10 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 100% 100% at 50% 50%, transparent 40%, #060a10 100%)' }}
      />

      {/* Moving scan bar */}
      <div className="absolute inset-0 z-10 overflow-hidden pointer-events-none">
        <ScanBar />
      </div>

      {/* ─── 3D ROBOT CANVAS ─────────────── */}
      <div className="absolute inset-0 z-10">
        {mounted && (
          <Suspense fallback={null}>
            <RobotScene cursorRef={cursorRef} />
          </Suspense>
        )}
      </div>

      {/* ─── HOTSPOTS ─────────────────────── */}
      <div className="absolute inset-0 z-20 pointer-events-none">
        <div className="relative w-full h-full pointer-events-auto">
          {HOTSPOTS.map(h => (
            <HotspotDot
              key={h.id}
              hotspot={h}
              onEnter={() => setActiveHotspot(h.id)}
              onLeave={() => setActiveHotspot(null)}
            />
          ))}
          <AnimatePresence>
            {activeHotspotData && <FeatureCard key={activeHotspotData.id} hotspot={activeHotspotData} />}
          </AnimatePresence>
        </div>
      </div>

      {/* ─── LEFT HUD ─────────────────────── */}
      <div className="absolute left-10 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-4">
        {['NEURAL CORE', 'AUDIO SCAN', 'SMS ENGINE', 'THREAT MAP'].map((label, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + i * 0.12 }}
            className="flex items-center gap-3 group cursor-pointer"
          >
            <div className="w-5 h-px bg-[#00e5ff] opacity-40 group-hover:opacity-100 group-hover:w-8 transition-all" />
            <span className="font-mono text-[0.58rem] text-[#3a5070] group-hover:text-[#00e5ff] uppercase tracking-[0.3em] transition-colors">{label}</span>
          </motion.div>
        ))}
      </div>

      {/* ─── HERO TEXT ─────────────────────── */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 text-center pointer-events-none" style={{ marginTop: '-15%' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="font-mono text-[0.6rem] uppercase tracking-[0.5em] text-[#00e5ff] mb-6 opacity-60"
        >
          Vishing & Smishing Defense Platform
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-6xl md:text-7xl font-bold tracking-tight leading-none mb-4"
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            background: 'linear-gradient(135deg, #ffffff 30%, #00e5ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            filter: 'drop-shadow(0 0 40px rgba(0,229,255,0.2))',
          }}
        >
          SENTINEL<br />
          <span style={{ fontSize: '0.55em', letterSpacing: '0.3em', opacity: 0.7 }}>AI</span>
        </motion.h1>
      </div>

      {/* ─── TOP RIGHT NAV ─────────────────── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="absolute top-8 right-10 z-20 flex gap-8"
      >
        {['Dashboard', 'SMS Scanner', 'Call Monitor', 'Legal'].map(item => (
          <a key={item} href="#" className="font-mono text-[0.62rem] text-[#3a5070] hover:text-[#00e5ff] uppercase tracking-[0.2em] transition-colors">{item}</a>
        ))}
      </motion.div>

      {/* ─── TOP LEFT LOGO ─────────────────── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="absolute top-8 left-10 z-20 flex items-center gap-3"
      >
        <div className="w-7 h-7 rounded border border-[#00e5ff]/40 flex items-center justify-center"
          style={{ background: 'rgba(0,229,255,0.08)' }}>
          <div className="w-2.5 h-2.5 rounded-full bg-[#00e5ff] animate-pulse shadow-[0_0_10px_#00e5ff]" />
        </div>
        <span className="font-mono text-[0.65rem] text-[#00e5ff]/70 uppercase tracking-[0.3em]">VSDP</span>
      </motion.div>

      {/* ─── BOTTOM CTA ────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="absolute bottom-20 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-4"
      >
        <a
          href="/login"
          className="px-8 py-3.5 rounded font-mono text-[0.7rem] text-[#060a10] font-bold uppercase tracking-[0.3em] transition-all hover:scale-105"
          style={{
            background: 'linear-gradient(135deg, #00e5ff, #0099bb)',
            boxShadow: '0 0 30px rgba(0,229,255,0.4), 0 0 60px rgba(0,229,255,0.1)',
          }}
        >
          Access Platform
        </a>
        <div className="font-mono text-[0.55rem] text-[#2a3a50] uppercase tracking-[0.4em]">
          Move cursor to interact with sentinel
        </div>
      </motion.div>

      {/* ─── BOTTOM HUD ─────────────────────── */}
      <HUDBar />
    </div>
  )
}
