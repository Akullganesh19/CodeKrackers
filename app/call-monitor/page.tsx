'use client'

import { useState, useEffect, useRef } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Phone, 
  Wifi, 
  Mic, 
  ShieldX, 
  AlertTriangle, 
  Zap, 
  Clock, 
  FileText,
  Activity,
  ArrowRight
} from 'lucide-react'

export default function CallMonitor() {
  const [seconds, setSeconds] = useState(0)
  const [transcript, setTranscript] = useState<{time: string, text: string, flagged?: boolean}[]>([])
  const [threatLevel, setThreatLevel] = useState(0)
  
  const transcriptLines = [
    { time: '00:04', text: "Hello, I am calling from TRAI head office...", flagged: false },
    { time: '00:09', text: "Your SIM card has been flagged for illegal activity...", flagged: true },
    { time: '00:14', text: "You must pay ₹5,000 fine immediately to avoid arrest...", flagged: true },
    { time: '00:19', text: "Please share your Aadhaar number for verification...", flagged: true },
  ]

  useEffect(() => {
    const timer = setInterval(() => setSeconds(s => s + 1), 1000)
    
    // Simulate transcript appearing
    transcriptLines.forEach((line, i) => {
      setTimeout(() => {
        setTranscript(prev => [...prev, line])
        if (line.flagged) setThreatLevel(prev => Math.min(prev + 25, 72))
      }, (i + 1) * 3000)
    })

    return () => clearInterval(timer)
  }, [])

  const formatTime = (s: number) => {
    const mins = Math.floor(s / 60)
    const secs = s % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Live Call Monitor" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* STATUS BAR */}
          <div className="flex justify-between items-center bg-surface2/50 border border-white/[0.03] p-8 rounded-lg backdrop-blur-md">
            <div className="flex items-center gap-10">
              <div className="space-y-1">
                <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Caller_Identity</div>
                <div className="font-mono text-xl text-white">+91-9872 042 108</div>
              </div>
              <div className="h-10 w-px bg-white/5" />
              <div className="space-y-1 text-center">
                <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Duration</div>
                <div className="font-space text-xl font-bold text-accent">{formatTime(seconds)}</div>
              </div>
            </div>
            <div className="flex items-center gap-4 px-6 py-2 rounded-full bg-success/5 border border-success/20">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse shadow-[0_0_10px_#7fff6e]" />
              <span className="font-mono text-[0.6rem] text-success uppercase tracking-[0.4em]">Monitoring_Active</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* THREAT GAUGE */}
            <div className="lg:col-span-4 vsdp-card p-12 flex flex-col items-center justify-center space-y-10 relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-success via-warning to-danger" />
               <div className="space-y-2 text-center">
                 <h3 className="font-space text-xl tracking-tight uppercase">Threat Matrix</h3>
                 <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Real-time heuristic analysis</div>
               </div>

               <div className="relative w-64 h-32 overflow-hidden mt-10">
                 <svg className="w-64 h-64 rotate-[-180deg]">
                   <circle cx="128" cy="128" r="100" fill="none" stroke="#111c2e" strokeWidth="20" strokeDasharray="314 314" />
                   <motion.circle 
                     cx="128" cy="128" r="100" fill="none" stroke="url(#gradient)" strokeWidth="20" 
                     strokeDasharray="314 314"
                     initial={{ strokeDashoffset: 314 }}
                     animate={{ strokeDashoffset: 314 - (314 * threatLevel) / 100 }}
                     transition={{ duration: 1.5, ease: "easeOut" }}
                   />
                   <defs>
                     <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                       <stop offset="0%" stopColor="#7fff6e" />
                       <stop offset="50%" stopColor="#f5c842" />
                       <stop offset="100%" stopColor="#ff3c6e" />
                     </linearGradient>
                   </defs>
                 </svg>
                 <div className="absolute inset-0 flex flex-col items-end justify-center pt-10">
                    <motion.div 
                      className="w-1.5 h-24 bg-white/40 origin-bottom rounded-full absolute bottom-0 left-[128px]"
                      animate={{ rotate: (threatLevel * 1.8) - 90 }}
                      transition={{ type: "spring", stiffness: 60 }}
                    />
                 </div>
               </div>

               <div className="text-center space-y-2">
                 <div className={`font-space text-6xl font-bold ${threatLevel > 60 ? 'text-danger' : threatLevel > 30 ? 'text-warning' : 'text-success'}`}>
                   {threatLevel}
                 </div>
                 <div className={`font-mono text-[0.7rem] uppercase tracking-[0.4em] font-bold ${threatLevel > 60 ? 'text-danger' : threatLevel > 30 ? 'text-warning' : 'text-success'}`}>
                   Threat Level: {threatLevel > 60 ? 'HIGH' : threatLevel > 30 ? 'CAUTION' : 'SAFE'}
                 </div>
                 <p className="font-mono text-[0.55rem] text-muted uppercase max-w-[200px] mx-auto leading-loose">
                   {threatLevel > 60 ? 'Suspicious patterns detected in audio stream' : 'Awaiting further speech data...'}
                 </p>
               </div>
            </div>

            {/* LIVE TRANSCRIPT */}
            <div className="lg:col-span-8 vsdp-card flex flex-col h-[500px]">
               <div className="p-8 border-b border-white/[0.03] flex justify-between items-center bg-white/[0.01]">
                 <div className="flex items-center gap-4">
                   <div className="w-2 h-2 rounded-full bg-danger animate-pulse" />
                   <h3 className="font-space text-xl tracking-tight uppercase">Live Transcript</h3>
                 </div>
                 <div className="flex items-center gap-6 font-mono text-[0.55rem] text-muted uppercase tracking-widest">
                   <div className="flex items-center gap-2">
                     <Mic size={12} className="text-accent" /> Whisper_STT
                   </div>
                   <div className="flex items-center gap-2">
                     <Wifi size={12} className="text-accent" /> Latency: 120ms
                   </div>
                 </div>
               </div>
               <div className="flex-1 overflow-y-auto p-10 space-y-6 scrollbar-hide">
                 <AnimatePresence>
                   {transcript.map((line, i) => (
                     <motion.div 
                       key={i}
                       initial={{ opacity: 0, x: -10 }}
                       animate={{ opacity: 1, x: 0 }}
                       className={`flex gap-6 p-4 rounded border transition-colors ${line.flagged ? 'bg-danger/5 border-danger/20' : 'bg-white/[0.02] border-white/5'}`}
                     >
                       <span className="font-mono text-[0.65rem] text-muted shrink-0">[{line.time}]</span>
                       <p className="font-mono text-sm leading-relaxed">
                         {line.text.split(' ').map((word, j) => {
                           const isFlagged = ['arrest', 'fine', 'aadhaar', 'trai', 'pay', '5,000'].includes(word.toLowerCase().replace(/[₹,]/g, ''))
                           return (
                             <span key={j} className={isFlagged ? 'bg-danger/40 text-white px-1' : ''}>
                               {word}{' '}
                             </span>
                           )
                         })}
                       </p>
                     </motion.div>
                   ))}
                 </AnimatePresence>
                 {transcript.length === 0 && (
                   <div className="h-full flex items-center justify-center font-mono text-[0.6rem] text-muted uppercase tracking-[0.4em] animate-pulse">
                     Initializing Audio Stream...
                   </div>
                 )}
               </div>
               
               {/* Waveform Decorator */}
               <div className="h-16 border-t border-white/[0.03] flex items-center justify-center gap-1 px-10">
                 {Array.from({ length: 60 }).map((_, i) => (
                   <WaveformBar key={i} />
                 ))}
               </div>
            </div>
          </div>

          {/* SIGNAL CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
             <SignalCard title="AI Voice Detected" sub="RawNet2 Inference" val="87%" color="danger" />
             <SignalCard title="Threat Keywords" sub="'arrest', 'fine', 'aadhaar'" val="Match" color="danger" />
             <SignalCard title="Caller Spoofed" sub="Not in TRAI whitelist" val="Warning" color="warning" />
             <SignalCard title="Deepfake Score" sub="GAN Artifact Detection" val="0.91" color="danger" />
          </div>

          {/* ACTION BUTTONS */}
          <div className="flex flex-wrap gap-8 pt-8 border-t border-white/[0.03]">
             <button className="btn-danger px-12 py-5 text-sm uppercase tracking-widest flex items-center gap-4">
               <ShieldX size={18} /> End & Block Call
             </button>
             <button className="btn-ghost border-warning/30 text-warning hover:bg-warning/5 px-12 py-5 text-sm uppercase tracking-widest flex items-center gap-4">
               <Zap size={18} /> Route to Honeypot
             </button>
             <button className="btn-ghost px-12 py-5 text-sm uppercase tracking-widest flex items-center gap-4">
               <FileText size={18} /> File FIR
             </button>
             <button className="btn-ghost px-12 py-5 text-sm uppercase tracking-widest flex items-center gap-4">
               <Activity size={18} /> Save Evidence
             </button>
          </div>
        </div>

        <style jsx>{`
          .scrollbar-hide::-webkit-scrollbar {
            display: none;
          }
          .scrollbar-hide {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }
        `}</style>
      </main>
    </div>
  )
}

function WaveformBar() {
  const [height, setHeight] = useState(20)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setHeight(Math.random() * 40 + 5)
    }, 100)
    return () => clearInterval(interval)
  }, [])

  return (
    <div 
      className="w-1 bg-accent/40 rounded-full transition-all duration-100" 
      style={{ height: `${height}px` }} 
    />
  )
}

function SignalCard({ title, sub, val, color }: any) {
  return (
    <div className={`vsdp-card p-8 space-y-4 border-t-2 ${color === 'danger' ? 'border-t-danger' : 'border-t-warning'}`}>
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <h4 className="font-space text-sm tracking-tight uppercase">{title}</h4>
          <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">{sub}</div>
        </div>
        <div className={`font-space text-lg font-bold ${color === 'danger' ? 'text-danger' : 'text-warning'}`}>{val}</div>
      </div>
      <div className={`h-1 w-full rounded-full bg-white/[0.03] overflow-hidden`}>
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: '80%' }}
          className={`h-full ${color === 'danger' ? 'bg-danger' : 'bg-warning'}`}
        />
      </div>
    </div>
  )
}
