'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Cpu, Database, BrainCircuit, Globe, Shield, Server, Wifi, Box, Code, Cloud, Lock, Zap } from 'lucide-react'

export default function TechStack() {
  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="System Architecture" />
        <div className="p-12 max-w-[1400px] mx-auto space-y-12">
          <div className="space-y-4">
            <div className="section-tag">Infrastructure Overview</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">System Architecture</h1>
          </div>

          {/* Architecture overview - 6 layers */}
          <div className="space-y-3">
            {[
              { title: 'User Layer', color: 'from-[#7c3aed] to-[#a78bfa]', items: ['React 19 · Next.js 16', 'Tailwind v4 · Framer Motion', 'React Three Fiber (3D)', 'Biometric Auth', 'PWA Support'], icon: Globe },
              { title: 'API Gateway', color: 'from-[#f59e0b] to-[#fbbf24]', items: ['FastAPI · Python 3.12', 'JWT + OAuth2', 'Rate Limiting (slowapi)', 'REST + WebSocket', 'CORS + CSP'], icon: Server },
              { title: 'AI / ML Engine', color: 'from-[#7c3aed] to-[#0aefff]', items: ['Groq Cloud (LLaMA 3.1)', 'DistilBERT (SMS)', 'Wav2Vec2 · RawNet2', 'Whisper (STT)', 'GAN Artifact Detector'], icon: BrainCircuit },
              { title: 'Intelligence Layer', color: 'from-[#10b981] to-[#34d399]', items: ['Scammer Reputation DB', 'Honeypot Bot Engine', 'Network Graph DB', 'Threat Scoring (0-100)', 'Real-time Alerting'], icon: Zap },
              { title: 'Data & Storage', color: 'from-[#64748b] to-[#94a3b8]', items: ['PostgreSQL 16', 'Redis 7 (Cache/Queue)', 'Blockchain (Tamper-proof)', 'AES-256 Encryption', '90-Day Rotation'], icon: Database },
              { title: 'Deployment', color: 'from-[#ff2056] to-[#ff5777]', items: ['Vercel (Frontend)', 'Render (Backend)', 'Docker · Kubernetes', 'AWS S3 (Assets)', 'CloudFlare (DNS/CDN)'], icon: Cloud },
            ].map((layer, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="glass-card p-6 md:p-8 group hover:border-[rgba(124,58,237,0.2)]"
              >
                <div className="flex flex-col md:flex-row md:items-center gap-6">
                  <div className="md:w-[180px] shrink-0 flex items-center gap-3">
                    <div className={`w-1 h-8 rounded-full bg-gradient-to-b ${layer.color} opacity-60`} />
                    <div className="flex items-center gap-2">
                      <layer.icon size={16} className="text-[#a78bfa]" />
                      <span className="font-mono text-[0.5rem] text-[#94a3b8] uppercase tracking-[0.3em]">{layer.title}</span>
                    </div>
                  </div>
                  <div className="flex-1 flex flex-wrap gap-2">
                    {layer.items.map((item, j) => (
                      <span key={j} className="chip chip-cyber text-[0.45rem]">{item}</span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { label: 'API Latency', val: '<180ms', color: 'text-[#10b981]' },
              { label: 'Model Inference', val: '42ms', color: 'text-[#0aefff]' },
              { label: 'Uptime SLA', val: '99.97%', color: 'text-[#a78bfa]' },
              { label: 'Threats Blocked', val: '2.6M+', color: 'text-[#ff2056]' },
            ].map((metric, i) => (
              <div key={i} className="glass-card p-6 text-center space-y-2">
                <div className="font-mono text-[0.45rem] text-[#64748b] uppercase tracking-widest">{metric.label}</div>
                <div className={`font-space text-3xl font-black ${metric.color}`}>{metric.val}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}