'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Phone, Mic, AlertTriangle, Shield, Headphones, Radio, Activity, Zap, Clock, Fingerprint } from 'lucide-react'

export default function CallMonitor() {
  const [isMonitoring, setIsMonitoring] = useState(false)

  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="Vishing Call Monitor" />
        <div className="p-12 max-w-[1400px] mx-auto space-y-12">
          <div className="space-y-4">
            <div className="section-tag">Real-time Audio Analysis</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">Call Monitoring</h1>
          </div>

          {/* Monitor Toggle */}
          <div className="glass-card p-12 flex flex-col items-center justify-center text-center space-y-8">
            <div className={`w-28 h-28 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
              isMonitoring ? 'border-[#ff2056] shadow-[0_0_40px_rgba(255,32,86,0.3)]' : 'border-[rgba(124,58,237,0.2)]'
            }`}>
              <Phone size={48} className={isMonitoring ? 'text-[#ff2056]' : 'text-[#64748b]'} />
            </div>
            <div className="space-y-4">
              <h2 className="font-space text-2xl uppercase tracking-tight">
                {isMonitoring ? 'Monitoring Active' : 'No Active Call'}
              </h2>
              <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.3em] max-w-md">
                {isMonitoring
                  ? 'AI analyzing audio for deepfake detection, voice cloning, and threat patterns'
                  : 'Connect a call to begin real-time AI-powered vishing detection'}
              </p>
            </div>
            <button
              onClick={() => setIsMonitoring(!isMonitoring)}
              className={isMonitoring ? 'btn-danger-cyber px-10 py-5 text-[0.55rem]' : 'btn-cyber px-10 py-5 text-[0.55rem]'}
            >
              <span>{isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}</span>
            </button>
          </div>

          {/* Capabilities Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Mic, title: 'Voice Clone Detection', desc: 'RawNet2 / Wav2Vec2 identifies AI-generated voice clones with 96.7% accuracy', color: 'text-[#ff2056]' },
              { icon: Fingerprint, title: 'GAN Artifact Scan', desc: 'Detects generative artifacts in real-time audio streams', color: 'text-[#a78bfa]' },
              { icon: Activity, title: 'NLP Intent Scanner', desc: 'Whisper-powered transcription analyzes for OTP/money requests', color: 'text-[#0aefff]' },
            ].map((item, i) => (
              <div key={i} className="glass-card p-8 space-y-6 group">
                <div className={`w-12 h-12 rounded-xl bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] flex items-center justify-center ${item.color} group-hover:scale-110 transition-transform`}>
                  <item.icon size={24} />
                </div>
                <h3 className={`font-space text-lg tracking-tight uppercase ${item.color}`}>{item.title}</h3>
                <p className="font-mono text-[0.5rem] text-[#64748b] leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}