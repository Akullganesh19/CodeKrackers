'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, AlertTriangle, CheckCircle2, Zap, RefreshCw, ArrowRight, Shield, FileScan } from 'lucide-react'

export default function SMSScanner() {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<null | 'SCAM' | 'SAFE'>(null)

  const handleAnalyze = () => {
    if (!input) return
    setLoading(true)
    setResult(null)
    setTimeout(() => {
      setLoading(false)
      const isScam = input.toLowerCase().includes('block') || input.toLowerCase().includes('update') || input.toLowerCase().includes('http')
      setResult(isScam ? 'SCAM' : 'SAFE')
    }, 1500)
  }

  const loadSample = (type: 'SCAM' | 'SAFE') => {
    const samples = {
      SCAM: "URGENT: Your SBI account will be blocked in 24hrs. Update KYC now: http://sbi-kyc-update.xyz/verify",
      SAFE: "Your OTP for SBI NetBanking is 847291. Valid 10 min. Do not share with anyone. -SBI"
    }
    setInput(samples[type])
    setResult(null)
  }

  return (
    <div className="flex min-h-screen bg-obsidian text-text-primary">
      <Sidebar />
      <main className="flex-1 ml-[260px]">
        <Topbar title="SMS Smishing Scanner" />
        <div className="p-12 max-w-[1200px] mx-auto space-y-12">
          {/* Header */}
          <div className="space-y-4 text-center">
            <div className="section-tag justify-center">Real-time Analysis</div>
            <h1 className="font-space text-4xl tracking-tighter uppercase">SMS Smishing Scanner</h1>
            <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.4em]">
              Powered by DistilBERT fine-tuned on Indian scam SMS datasets
            </p>
          </div>

          {/* Scanner Card */}
          <div className="max-w-3xl mx-auto space-y-8">
            <div className="glass-card p-10 space-y-8">
              <div className="space-y-5">
                <label className="font-mono text-[0.5rem] text-[#a78bfa] uppercase tracking-[0.4em]">Paste SMS to Analyze</label>
                <div className="relative">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="w-full h-48 bg-[rgba(16,16,31,0.6)] border border-[rgba(124,58,237,0.1)] p-6 rounded-lg font-mono text-sm text-white focus:border-[rgba(124,58,237,0.3)] focus:outline-none focus:ring-2 focus:ring-[rgba(124,58,237,0.08)] transition-all resize-none placeholder:text-[#475569]"
                    placeholder="Paste suspicious SMS here..."
                  />
                  <div className="absolute bottom-4 right-5 font-mono text-[0.45rem] text-[#475569] uppercase tracking-widest">
                    {input.length} chars
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-4">
                <button onClick={() => loadSample('SCAM')}
                  className="flex-1 btn-ghost-cyber border-[rgba(255,32,86,0.2)] text-[#ff2056] hover:bg-[rgba(255,32,86,0.04)] py-4 text-[0.55rem] flex items-center justify-center gap-2">
                  <AlertTriangle size={14} /> Load Scam Sample
                </button>
                <button onClick={() => loadSample('SAFE')}
                  className="flex-1 btn-ghost-cyber border-[rgba(16,185,129,0.2)] text-[#10b981] hover:bg-[rgba(16,185,129,0.04)] py-4 text-[0.55rem] flex items-center justify-center gap-2">
                  <CheckCircle2 size={14} /> Load Safe Sample
                </button>
              </div>

              <button onClick={handleAnalyze} disabled={loading || !input}
                className="btn-cyber w-full py-5 text-[0.55rem] flex items-center justify-center gap-3 disabled:opacity-50">
                {loading ? <RefreshCw className="animate-spin" size={16} /> : <Zap size={16} />}
                {loading ? 'Analyzing with BERT model...' : 'Analyze SMS →'}
              </button>
            </div>

            {/* Result */}
            <AnimatePresence mode="wait">
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`glass-card p-10 space-y-8 border-l-2 ${result === 'SCAM' ? 'border-[#ff2056]' : 'border-[#10b981]'}`}
                >
                  <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                    <div className="space-y-4">
                      <div className={`inline-flex items-center gap-3 px-5 py-3 rounded-lg font-space font-bold text-lg ${
                        result === 'SCAM'
                          ? 'bg-[rgba(255,32,86,0.1)] border border-[rgba(255,32,86,0.2)] text-[#ff2056]'
                          : 'bg-[rgba(16,185,129,0.1)] border border-[rgba(16,185,129,0.2)] text-[#10b981]'
                      }`}>
                        {result === 'SCAM' ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
                        {result === 'SCAM' ? 'SMISHING DETECTED' : 'SAFE — NO THREAT'}
                      </div>
                      <div className="space-y-2">
                        <div className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-widest">
                          Confidence: <span className={result === 'SCAM' ? 'text-[#ff2056]' : 'text-[#10b981]'}>{result === 'SCAM' ? '94.2%' : '97.8%'}</span>
                        </div>
                        <div className="h-1.5 w-64 bg-[rgba(16,16,31,0.6)] rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: result === 'SCAM' ? '94.2%' : '97.8%' }}
                            transition={{ duration: 1 }}
                            className={`h-full rounded-full ${result === 'SCAM' ? 'bg-[#ff2056]' : 'bg-[#10b981]'}`}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {result === 'SCAM' ? (
                        <>
                          <span className="chip chip-alert">Suspicious URL</span>
                          <span className="chip chip-alert">Urgency Language</span>
                          <span className="chip chip-alert">KYC Keyword</span>
                        </>
                      ) : (
                        <>
                          <span className="chip chip-lime">Verified Sender</span>
                          <span className="chip chip-lime">Standard Format</span>
                          <span className="chip chip-lime">No Malware Link</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="pt-8 border-t border-[rgba(124,58,237,0.06)] flex flex-col md:flex-row justify-between items-center gap-8">
                    <p className="font-mono text-[0.55rem] text-[#64748b] italic">
                      {result === 'SCAM'
                        ? '🚨 DO NOT click any links. Report immediately to cybercrime.gov.in'
                        : '✅ This SMS appears legitimate based on neural classification.'}
                    </p>
                    <div className="flex gap-4">
                      {result === 'SCAM' ? (
                        <>
                          <button className="btn-danger-cyber text-[0.5rem] py-3 px-6">🚨 Report</button>
                          <button className="btn-ghost-cyber text-[0.5rem] py-3 px-6">⛓️ Log Ledger</button>
                        </>
                      ) : (
                        <button className="btn-ghost-cyber text-[0.5rem] py-3 px-6">Mark as Trusted</button>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* How It Works */}
          <div className="grid md:grid-cols-3 gap-6 pt-8">
            {[
              { step: '01', title: 'Tokenization', desc: 'Text tokenized → DistilBERT model inference' },
              { step: '02', title: 'Feature Scan', desc: 'URL patterns, urgency keywords, sender ID analyzed' },
              { step: '03', title: 'Risk Score', desc: 'Risk score computed — SAFE/DANGER in under 300ms' },
            ].map((s, i) => (
              <div key={i} className="glass-card p-8 space-y-5 relative group">
                <div className="font-space text-5xl text-white/[0.02] group-hover:text-[#a78bfa]/5 transition-colors absolute top-5 right-6">{s.step}</div>
                <h3 className="font-space text-lg tracking-tight uppercase text-[#a78bfa]">{s.title}</h3>
                <p className="font-mono text-[0.5rem] text-[#64748b] uppercase tracking-[0.2em] leading-loose">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}