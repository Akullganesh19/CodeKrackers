'use client'

import React, { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { Oracle } from '@/app/lib/oracle'
import {
  ShieldAlert,
  ShieldCheck,
  Search,
  AlertTriangle,
  ChevronRight,
  ExternalLink,
  Database,
  Cpu,
  BarChart3,
  Loader2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function SMSScannerPage() {
  const [mounted, setMounted] = useState(false)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<null | {
    isScam: boolean;
    confidence: number;
    riskFactors: string[];
    recommendation: string;
    tags: string[];
  }>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    // 🛸 Oracle: Predict intent when user stops typing for 800ms
    const timer = setTimeout(() => {
      if (text.length > 15 && !loading) {
        Oracle.predictSmsScan(text);
      }
    }, 800);
    return () => clearTimeout(timer);
  }, [text, loading]);

  const handleAnalyze = async () => {
    if (!text.trim()) return

    setLoading(true)
    setResult(null)

    try {
      // 🛸 Oracle: Check for pre-computed result first
      const predictedResult = await Oracle.resolveSmsScan(text);
      if (predictedResult) {
        setResult(predictedResult);
        setLoading(false);
        return;
      }

      const token = localStorage.getItem('vsdp_token') || 'dummy_token';
      const response = await fetch('http://localhost:8000/api/analytics/scan', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text })
      });
      
      console.log("Response Status:", response.status);
      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert('Failed to analyze SMS');
    } finally {
      setLoading(false)
    }
  }

  const loadSample = (type: 'scam' | 'safe') => {
    if (type === 'scam') {
      setText("URGENT: Your HDFC Bank account has been blocked due to suspicious activity. Click here to update your KYC immediately: http://bit.ly/hdfc-kyc-update")
    } else {
      setText("Hi Rahul, we are meeting at 6 PM for dinner at the new cafe. Let me know if you are joining.")
    }
  }

  const handleReportToCybercrime = async () => {
    if (!result) return;
    try {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token';
      const response = await fetch('http://localhost:8000/api/blacklist/report', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          identifier: text.substring(0, 50) + "...", // Hashed in backend usually, or identifier of sender
          type: "phone",
          reason: "User reported Smishing: " + result.recommendation
        })
      });
      if (response.ok) {
        alert("Reported to global blacklist successfully.");
      }
    } catch(err) {
      alert("Failed to report.");
    }
  }

  const handleBlockchainLog = async () => {
    if (!result) return;
    try {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token';
      const url = new URL('http://localhost:8000/api/zk/sealed-report');
      url.searchParams.append('report_data', JSON.stringify({ content: text, analysis: result }));
      
      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      if (response.ok) {
        alert(`⛓️ BLOCKCHAIN LOGGED: Receipt: ${data.report_hash.substring(0, 16)}... Evidence is now immutable.`);
      } else {
        alert("Blockchain logging failed.");
      }
    } catch(err) {
      alert("Error contacting blockchain relayer.");
    }
  }

  if (!mounted) return null

  return (
    <div className="flex min-h-screen bg-bg text-white selection:bg-cyan-500/30">
      <Sidebar />
      <main className="flex-1 ml-[240px] flex flex-col">
        <Topbar title="SMS Scanner" />

        <div className="flex-1 p-10 max-w-5xl mx-auto w-full space-y-10">

          <div className="vsdp-card p-0 overflow-hidden relative">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500" />

            <div className="p-8 space-y-6">
              <div className="flex items-center gap-4 text-cyan-400">
                <Search size={24} />
                <h2 className="font-space text-2xl font-bold uppercase tracking-tight">Paste Message Data</h2>
              </div>

              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Initialize input sequence..."
                className="w-full h-40 bg-black/40 border border-white/10 rounded-lg p-6 font-mono text-sm resize-none focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all text-white/80 placeholder:text-white/20"
              />

              <div className="flex gap-4">
                <button
                  onClick={() => loadSample('scam')}
                  className="px-4 py-2 rounded border border-red-500/30 text-red-400 font-mono text-[0.65rem] uppercase tracking-wider hover:bg-red-500/10 transition-colors flex items-center gap-2"
                >
                  <AlertTriangle size={12} /> Load Scam Sample
                </button>
                <button
                  onClick={() => loadSample('safe')}
                  className="px-4 py-2 rounded border border-green-500/30 text-green-400 font-mono text-[0.65rem] uppercase tracking-wider hover:bg-green-500/10 transition-colors flex items-center gap-2"
                >
                  <ShieldCheck size={12} /> Load Safe Sample
                </button>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={loading || !text.trim()}
                className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-muted/20 disabled:text-muted/50 text-bg font-black uppercase tracking-widest py-4 rounded-md transition-all flex items-center justify-center gap-3 active:scale-[0.98]"
              >
                {loading ? 'Processing...' : 'ANALYZE SMS →'}
              </button>
            </div>

            {/* Loading Overlay */}
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 bg-bg/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-6"
                >
                  <div className="relative w-20 h-20">
                    <Loader2 className="w-20 h-20 text-cyan-400 animate-spin" />
                    <motion.div
                      animate={{ top: ['0%', '100%', '0%'] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      className="absolute left-0 w-full h-0.5 bg-cyan-400/50 shadow-[0_0_10px_#22d3ee]"
                    />
                  </div>
                  <div className="text-center space-y-2">
                    <p className="font-mono text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase animate-pulse">
                      Analyzing with BERT model...
                    </p>
                    <div className="flex gap-1 justify-center">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          animate={{ scale: [1, 1.5, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.2 }}
                          className="w-1 h-1 bg-cyan-400 rounded-full"
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Result Panel */}
            <AnimatePresence>
              {result && !loading && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  className="border-t border-white/5 bg-white/[0.01]"
                >
                  <div className="p-8 space-y-8">
                    {result.isScam ? (
                      <div className="space-y-6">
                        <div className="flex items-center gap-4">
                          <div className="bg-red-500/10 border border-red-500/30 px-6 py-3 rounded-md text-red-500 font-space font-bold uppercase tracking-widest flex items-center gap-3 text-lg">
                            <ShieldAlert size={24} /> ⚠️ SMISHING DETECTED
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between font-mono text-[0.65rem] uppercase tracking-widest text-muted">
                            <span>Scam Confidence</span>
                            <span>{result.confidence}%</span>
                          </div>
                          <div className="h-2 w-full bg-surface rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${result.confidence}%` }}
                              transition={{ duration: 1, ease: "easeOut" }}
                              className="h-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"
                            />
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest font-bold">Risk Factors</div>
                          <div className="flex flex-wrap gap-2">
                            {(result.riskFactors || []).map((factor, i) => (
                              <span key={i} className="node-chip-red text-[0.65rem]">[{factor}]</span>
                            ))}
                          </div>
                        </div>

                        <div className="p-4 bg-red-500/5 border-l-2 border-red-500 rounded-r-md">
                          <p className="text-red-300 text-sm font-medium">{result.recommendation}</p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4 pt-4">
                          <button 
                            onClick={handleReportToCybercrime}
                            className="btn-danger flex items-center justify-center gap-2 text-xs uppercase font-bold tracking-widest"
                          >
                            🚨 Report to Cybercrime Portal
                          </button>
                          <button 
                            onClick={handleBlockchainLog}
                            className="btn-ghost flex items-center justify-center gap-2 text-xs uppercase font-bold tracking-widest border-white/10 text-white/70"
                          >
                            ⛓️ Log on Blockchain
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        <div className="bg-green-500/5 border border-green-500/30 px-6 py-3 rounded-md text-green-500 font-space font-bold uppercase tracking-widest flex items-center gap-3 text-lg">
                          <ShieldCheck size={24} /> ✅ SAFE — NO THREAT DETECTED
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between font-mono text-[0.65rem] uppercase tracking-widest text-muted">
                            <span>Legitimacy Confidence</span>
                            <span>{result.confidence}%</span>
                          </div>
                          <div className="h-2 w-full bg-surface rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${result.confidence}%` }}
                              transition={{ duration: 1, ease: "easeOut" }}
                              className="h-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"
                            />
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-2">
                          {(result.tags || []).map((tag, i) => (
                            <span key={i} className="node-chip-green text-[0.65rem]">[{tag}]</span>
                          ))}
                        </div>

                        <p className="text-green-300/80 text-sm italic">{result.recommendation}</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* How it Works Section */}
          <div className="space-y-8">
            <div className="flex items-center gap-6">
              <h2 className="font-space text-2xl font-black uppercase italic italic">HOW IT WORKS</h2>
              <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: 'Step 1: NLP Processing',
                  desc: 'Text is tokenized and processed through a DistilBERT model inference engine.',
                  icon: Cpu,
                  tag: 'TOKENIZATION'
                },
                {
                  title: 'Step 2: Heuristic Analysis',
                  desc: 'URL patterns, urgency keywords, and sender ID are cross-referenced with threat databases.',
                  icon: Database,
                  tag: 'PATTERN MATCH'
                },
                {
                  title: 'Step 3: Scoring',
                  desc: 'A multi-vector risk score is computed to classify the SMS in under 300ms.',
                  icon: BarChart3,
                  tag: 'INFERENCE'
                }
              ].map((step, i) => (
                <div key={i} className="vsdp-card p-8 group hover:translate-y-[-4px]">
                  <div className="font-mono text-[0.6rem] text-accent font-bold tracking-widest mb-4">[{step.tag}]</div>
                  <div className="p-3 bg-accent/5 border border-accent/20 rounded-lg w-fit mb-6 group-hover:bg-accent/10 transition-colors">
                    <step.icon className="text-accent" size={24} />
                  </div>
                  <h3 className="font-space text-lg font-bold mb-3 uppercase tracking-tight">{step.title}</h3>
                  <p className="font-mono text-xs text-muted leading-relaxed">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
