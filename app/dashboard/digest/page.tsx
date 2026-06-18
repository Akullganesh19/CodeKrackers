'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Shield, ShieldAlert, Activity, Award } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useAuth } from '@/backend/core/AuthProvider'

export default function PersonalDigest() {
  const [mounted, setMounted] = useState(false)
  const [digest, setDigest] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    async function fetchDigest() {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null
        const res = await fetch('http://localhost:8000/api/analytics/personal-digest', {
          headers: { 'Authorization': `Bearer ${token || 'dummy_token'}` }
        })
        if (res.ok) {
          const data = await res.json()
          setDigest(data)
        }
      } catch (err) {
        console.error("Failed to fetch digest:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchDigest()
  }, [])

  if (!mounted) return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="flex min-h-screen bg-bg text-white">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="My Defense Digest" />

        <div className="p-10 space-y-10 max-w-[1200px] mx-auto">
          {/* HEADLINE METRICS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="vsdp-card p-8 flex items-center justify-between border-l-4 border-accent">
              <div className="space-y-2">
                <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">Current Safety Score</div>
                <div className="font-space text-4xl font-bold">{loading ? '--' : digest?.safety_score?.toFixed(1) || '100.0'}</div>
              </div>
              <Activity size={32} className="text-accent opacity-50" />
            </div>

            <div className="vsdp-card p-8 flex items-center justify-between border-l-4 border-success">
              <div className="space-y-2">
                <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">Total Threats Blocked</div>
                <div className="font-space text-4xl font-bold">{loading ? '--' : digest?.total_threats_blocked || '0'}</div>
              </div>
              <Shield size={32} className="text-success opacity-50" />
            </div>

            <div className="vsdp-card p-8 flex items-center justify-between border-l-4 border-warning">
              <div className="space-y-2">
                <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">Scams Avoided</div>
                <div className="font-space text-4xl font-bold">{loading ? '--' : digest?.scams_avoided || '0'}</div>
              </div>
              <Award size={32} className="text-warning opacity-50" />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {/* THREAT BREAKDOWN */}
            <div className="vsdp-card p-8 space-y-6">
              <h3 className="font-space text-lg uppercase tracking-tight flex items-center gap-2">
                <ShieldAlert size={16} className="text-accent" />
                Your Blocked Threats
              </h3>

              <div className="space-y-4">
                {loading ? (
                  <div className="font-mono text-sm text-muted">Loading...</div>
                ) : !digest?.threat_breakdown || Object.keys(digest.threat_breakdown).length === 0 ? (
                  <div className="p-4 border border-white/5 bg-white/[0.02] rounded font-mono text-sm text-muted">
                    No threats detected yet. Your lines are secure.
                  </div>
                ) : (
                  Object.entries(digest.threat_breakdown).map(([type, count]: [string, any], i) => (
                    <div key={i} className="flex items-center justify-between p-4 border border-white/5 bg-white/[0.01] hover:bg-white/[0.03] transition-colors rounded">
                      <span className="font-mono text-[0.7rem] uppercase text-white/80">{type}</span>
                      <span className="font-space font-bold text-accent">{count} Blocked</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* SCORE HISTORY GRAPH (Simplified) */}
            <div className="vsdp-card p-8 space-y-6">
              <h3 className="font-space text-lg uppercase tracking-tight flex items-center gap-2">
                <Activity size={16} className="text-success" />
                Score History (Last 30 Days)
              </h3>

              <div className="h-48 flex items-end justify-between gap-2 px-2 pb-4 border-b border-white/10 relative">
                {loading ? (
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-sm text-muted">Loading...</div>
                ) : !digest?.score_history || digest.score_history.length === 0 ? (
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-sm text-muted">No historical data available.</div>
                ) : (
                  digest.score_history.map((h: any, i: number) => {
                    const heightPercent = (h.score / 100) * 100;
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center justify-end gap-2 group h-full">
                        <div className="w-full relative h-full flex items-end">
                           <motion.div
                             initial={{ height: 0 }}
                             animate={{ height: `${heightPercent}%` }}
                             className="w-full max-w-[24px] mx-auto bg-success/20 border-t-2 border-success group-hover:bg-success/40 transition-colors"
                           />
                           <div className="absolute -top-8 left-1/2 -translate-x-1/2 font-mono text-[0.5rem] opacity-0 group-hover:opacity-100 transition-opacity bg-success text-black px-1 rounded z-10">
                             {h.score.toFixed(0)}
                           </div>
                        </div>
                        <span className="font-mono text-[0.45rem] text-muted uppercase tracking-tighter truncate w-full text-center">{h.date}</span>
                      </div>
                    )
                  })
                )}
              </div>
              <div className="text-right font-mono text-[0.55rem] text-muted">
                Score fluctuates based on proactive reporting and honeypot participation.
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
