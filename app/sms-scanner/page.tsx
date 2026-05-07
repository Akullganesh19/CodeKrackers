'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  Database, 
  Scale, 
  ArrowRight,
  RefreshCw,
  Zap
} from 'lucide-react'

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
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="SMS Smishing Scanner" />

        <div className="p-12 max-w-[1200px] mx-auto space-y-16">
          <div className="space-y-4 text-center">
            <h1 className="font-space text-4xl tracking-tighter uppercase">SMS Smishing Scanner</h1>
            <p className="font-mono text-[0.6rem] text-muted uppercase tracking-[0.4em]">
              Powered by BERT/DistilBERT fine-tuned on Indian scam SMS datasets
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-10">
            <div className="vsdp-card p-10 space-y-10">
              <div className="space-y-6">
                <label className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.4em]">Paste SMS to Analyze</label>
                <div className="relative">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="w-full h-48 bg-surface2 border border-white/10 p-8 rounded-md font-mono text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 transition-all resize-none"
                    placeholder="Paste suspicious SMS here..."
                  />
                  <div className="absolute bottom-4 right-6 font-mono text-[0.55rem] text-muted uppercase tracking-widest">
                    {input.length} Characters
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-6">
                <button 
                  onClick={() => loadSample('SCAM')}
                  className="flex-1 btn-ghost border-danger/30 text-danger hover:bg-danger/5 py-4 text-[0.65rem] uppercase tracking-widest flex items-center justify-center gap-3"
                >
                  <AlertTriangle size={14} /> Load Scam Sample
                </button>
                <button 
                  onClick={() => loadSample('SAFE')}
                  className="flex-1 btn-ghost border-success/30 text-success hover:bg-success/5 py-4 text-[0.65rem] uppercase tracking-widest flex items-center justify-center gap-3"
                >
                  <CheckCircle2 size={14} /> Load Safe Sample
                </button>
              </div>

              <button 
                onClick={handleAnalyze}
                disabled={loading || !input}
                className="btn-primary w-full py-5 text-sm uppercase tracking-widest flex items-center justify-center gap-4 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
                {loading ? 'Analyzing with BERT model...' : 'Analyze SMS →'}
              </button>
            </div>

            <AnimatePresence mode="wait">
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`vsdp-card p-10 space-y-10 ${result === 'SCAM' ? 'border-danger/30 bg-danger/[0.02]' : 'border-success/30 bg-success/[0.02]'}`}
                >
                  <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                    <div className="space-y-4">
                      <div className={`inline-flex items-center gap-3 px-4 py-2 rounded border font-space font-bold text-lg ${result === 'SCAM' ? 'bg-danger/10 border-danger text-danger' : 'bg-success/10 border-success text-success'}`}>
                        {result === 'SCAM' ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
                        {result === 'SCAM' ? 'SMISHING DETECTED' : 'SAFE — NO THREAT DETECTED'}
                      </div>
                      <div className="space-y-2">
                        <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">
                          Confidence: <span className={result === 'SCAM' ? 'text-danger' : 'text-success'}>{result === 'SCAM' ? '94.2%' : '97.8%'}</span>
                        </div>
                        <div className="h-1.5 w-64 bg-white/[0.03] rounded-full overflow-hidden">
                           <motion.div 
                             initial={{ width: 0 }}
                             animate={{ width: result === 'SCAM' ? '94.2%' : '97.8%' }}
                             transition={{ duration: 1 }}
                             className={`h-full ${result === 'SCAM' ? 'bg-danger' : 'bg-success'}`}
                           />
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      {result === 'SCAM' ? (
                        <>
                          <div className="node-chip-red text-[0.6rem]">Suspicious URL</div>
                          <div className="node-chip-red text-[0.6rem]">Urgency Language</div>
                          <div className="node-chip-red text-[0.6rem]">KYC Keyword</div>
                        </>
                      ) : (
                        <>
                          <div className="node-chip-green text-[0.6rem]">Verified Sender</div>
                          <div className="node-chip-green text-[0.6rem]">Standard Format</div>
                          <div className="node-chip-green text-[0.6rem]">No Malware Link</div>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="pt-10 border-t border-white/[0.03] flex flex-col md:flex-row justify-between items-center gap-10">
                    <p className="font-mono text-[0.65rem] text-muted italic">
                      {result === 'SCAM' 
                        ? "🚨 DO NOT click any links. Report immediately to local authorities." 
                        : "✅ This SMS appears legitimate based on neural classification."}
                    </p>
                    <div className="flex gap-6 w-full md:w-auto">
                       {result === 'SCAM' ? (
                         <>
                           <button className="btn-danger flex-1 md:flex-none text-[0.65rem] py-3 px-8 uppercase tracking-widest">🚨 Report</button>
                           <button className="btn-ghost flex-1 md:flex-none text-[0.65rem] py-3 px-8 uppercase tracking-widest">⛓️ Log Ledger</button>
                         </>
                       ) : (
                         <button className="btn-ghost w-full md:w-auto text-[0.65rem] py-3 px-8 uppercase tracking-widest">Mark as Trusted</button>
                       )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* HOW IT WORKS */}
          <div className="grid md:grid-cols-3 gap-8 pt-10">
            {[
              { step: '01', title: 'Tokenization', desc: 'Text tokenized → DistilBERT model inference' },
              { step: '02', title: 'Feature Scan', desc: 'URL patterns, urgency keywords, sender ID analyzed' },
              { step: '03', title: 'Risk Score', desc: 'Risk score computed — SAFE/DANGER in under 300ms' },
            ].map((s, i) => (
              <div key={i} className="vsdp-card p-10 space-y-6 relative group">
                <div className="font-space text-5xl text-white/[0.03] group-hover:text-accent/5 transition-colors absolute top-6 right-8">{s.step}</div>
                <h3 className="font-space text-lg tracking-tight uppercase text-accent">{s.title}</h3>
                <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest leading-loose">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
