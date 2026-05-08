'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { 
  Cpu, 
  Database, 
  Globe, 
  MessageSquare, 
  Mic, 
  ShieldCheck, 
  Zap, 
  Code2,
  Layers,
  Search,
  Activity
} from 'lucide-react'

import React from 'react'

export default function TechStack() {
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const models = [
    {
      name: 'BERT / DistilBERT',
      task: 'SMS Smishing Detection',
      icon: <MessageSquare size={24} />,
      color: 'accent',
      stats: [
        { label: 'Accuracy', val: '97.2%' },
        { label: 'Latency', val: '42ms' },
        { label: 'Parameters', val: '66M' },
      ],
      desc: 'Fine-tuned on 200k+ Indian context SMS messages including e-challan, KYC, and bank fraud patterns.'
    },
    {
      name: 'RawNet2 / Wav2Vec2',
      task: 'Vishing Deepfake Detection',
      icon: <Mic size={24} />,
      color: 'danger',
      stats: [
        { label: 'GAN Detection', val: '0.94' },
        { label: 'Inference', val: '120ms' },
        { label: 'Frequency', val: '16kHz' },
      ],
      desc: 'Detects synthetic artifacts in audio streams. Used to identify AI voice cloning in real-time calls.'
    },
    {
      name: 'OpenAI Whisper',
      task: 'Speech-to-Text (STT)',
      icon: <Activity size={24} />,
      color: 'warning',
      stats: [
        { label: 'WER', val: '<12%' },
        { label: 'Multilingual', val: '99+' },
        { label: 'Streaming', val: 'Active' },
      ],
      desc: 'Real-time transcription of calls into text for NLP-based threat heuristic analysis.'
    },
    {
      name: 'Llama-3-Legal',
      task: 'FIR Auto-Drafting',
      icon: <Code2 size={24} />,
      color: 'success',
      stats: [
        { label: 'Indian IT Act', val: 'Fine-tuned' },
        { label: 'Context Win', val: '8k' },
        { label: 'Draft Time', val: '2.4s' },
      ],
      desc: 'Specially fine-tuned on the Indian Penal Code and IT Act 2000 to generate courtroom-ready documents.'
    }
  ]

  if (!mounted) return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
      <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.5em] animate-pulse">Mapping_Neural_Architecture...</div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Technical Architecture & Models" />

        <div className="p-12 space-y-16 max-w-[1400px] mx-auto">
          {/* HEADER */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8">
            <div className="space-y-4">
              <div className="section-tag">Infrastructure</div>
              <h1 className="font-space text-4xl tracking-tighter uppercase">AI/ML Intelligence Stack</h1>
              <p className="font-mono text-[0.65rem] text-muted uppercase tracking-widest italic max-w-xl">
                A multi-layered defense architecture combining neural text classification, 
                acoustic deepfake detection, and blockchain evidence logging.
              </p>
            </div>
            <div className="flex gap-4">
              <div className="px-6 py-3 border border-white/5 bg-surface2 rounded-md font-mono text-[0.55rem] text-muted uppercase tracking-widest">
                Stack Version: v2.4.0-Sentinel
              </div>
            </div>
          </div>

          {/* AI MODELS GRID */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {models.map((model, i) => (
              <div key={i} className="vsdp-card p-10 space-y-8 relative group">
                <div className={`absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity ${model.color === 'accent' ? 'text-accent' : model.color === 'danger' ? 'text-danger' : model.color === 'warning' ? 'text-warning' : 'text-success'}`}>
                  {model.icon}
                </div>
                
                <div className="space-y-4">
                  <div className={`font-mono text-[0.6rem] uppercase tracking-[0.3em] ${model.color === 'accent' ? 'text-accent' : model.color === 'danger' ? 'text-danger' : model.color === 'warning' ? 'text-warning' : 'text-success'}`}>
                    {model.task}
                  </div>
                  <h3 className="font-space text-2xl tracking-tight uppercase font-bold">{model.name}</h3>
                  <p className="font-inter text-sm text-muted leading-relaxed italic">
                    "{model.desc}"
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-6 pt-6 border-t border-white/[0.03]">
                   {model.stats.map((s, j) => (
                     <div key={j} className="space-y-1">
                        <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">{s.label}</div>
                        <div className="font-space font-bold text-lg">{s.val}</div>
                     </div>
                   ))}
                </div>
              </div>
            ))}
          </div>

          {/* SYSTEM ARCHITECTURE MODULE */}
          <div className="vsdp-card p-12 space-y-12">
             <div className="space-y-4">
               <h3 className="font-space text-2xl tracking-tight uppercase">Platform Infrastructure</h3>
               <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">Integrated Hybrid Cloud & Edge Deployment</div>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                <TechModule 
                  icon={<Layers size={20} />} 
                  title="Frontend / HUD" 
                  tech={['Next.js 15', 'Tailwind CSS', 'Framer Motion', 'Lucide Icons']} 
                  desc="High-fidelity cybersecurity interface with real-time HUD and telemetry visualization."
                />
                <TechModule 
                  icon={<Database size={20} />} 
                  title="Backend / API" 
                  tech={['FastAPI (Python)', 'Redis (Queue)', 'PostgreSQL', 'WebSockets']} 
                  desc="Asynchronous high-performance API handling model inference and live streaming data."
                />
                <TechModule 
                  icon={<Globe size={20} />} 
                  title="Data / Blockchain" 
                  tech={['Hyperledger Fabric', 'AWS S3 (Encrypted)', 'AES-256-GCM', 'TLS 1.3']} 
                  desc="Immutable evidence ledger for forensic storage and regulatory compliance."
                />
             </div>
          </div>

          {/* BOTTOM TAGS */}
          <div className="flex flex-wrap gap-8 justify-center pt-8 opacity-40">
             <div className="flex items-center gap-3 font-mono text-[0.55rem] uppercase tracking-[0.4em]">
               <ShieldCheck size={14} /> CERT-In Ready
             </div>
             <div className="flex items-center gap-3 font-mono text-[0.55rem] uppercase tracking-[0.4em]">
               <Zap size={14} /> India AI Mission
             </div>
             <div className="flex items-center gap-3 font-mono text-[0.55rem] uppercase tracking-[0.4em]">
               <Cpu size={14} /> GPU Optimized (A100)
             </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function TechModule({ icon, title, tech, desc }: any) {
  return (
    <div className="space-y-6 group">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded bg-accent/5 border border-accent/20 flex items-center justify-center text-accent group-hover:bg-accent/10 transition-colors">
          {icon}
        </div>
        <h4 className="font-space text-lg tracking-tight uppercase">{title}</h4>
      </div>
      <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest leading-loose">
        {desc}
      </p>
      <div className="flex flex-wrap gap-2">
        {tech.map((t: string, i: number) => (
          <div key={i} className="node-chip text-[0.45rem]">{t}</div>
        ))}
      </div>
    </div>
  )
}
