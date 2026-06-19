'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Target, Clock, ShieldCheck, AlertTriangle } from 'lucide-react'

export default function PersonalThreatInsights() {
  const [insights, setInsights] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchInsights() {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null
        const res = await fetch('http://localhost:8000/api/v1/analytics/personal-insights', {
          headers: { 'Authorization': `Bearer ${token || 'dummy_token'}` }
        })
        if (res.ok) {
          const data = await res.json()
          setInsights(data)
        }
      } catch (err) {
        console.error("Failed to fetch personal insights", err)
      } finally {
        setLoading(false)
      }
    }
    fetchInsights()
  }, [])

  if (loading) {
    return (
      <div className="vsdp-card p-8 flex items-center justify-center min-h-[250px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
          <div className="font-mono text-[0.6rem] text-muted uppercase tracking-widest animate-pulse">Loading Insights...</div>
        </div>
      </div>
    )
  }

  if (!insights || !insights.has_data) {
    return (
      <div className="vsdp-card p-8 flex flex-col items-center justify-center min-h-[250px] text-center space-y-4">
        <ShieldCheck size={48} className="text-success/50" />
        <div>
          <h3 className="font-space text-lg font-bold tracking-tight uppercase">No Threats Detected</h3>
          <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest mt-2 max-w-[250px]">
            Your communication channels are currently secure. Keep your shields up.
          </p>
        </div>
        {insights && (
          <div className="flex gap-6 mt-4">
            <div className="text-center">
              <div className="font-space text-xl font-bold text-accent">{insights.safety_score}%</div>
              <div className="font-mono text-[0.5rem] text-muted uppercase">Safety Score</div>
            </div>
            <div className="text-center">
              <div className="font-space text-xl font-bold text-success">{insights.scams_avoided}</div>
              <div className="font-mono text-[0.5rem] text-muted uppercase">Scams Avoided</div>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="vsdp-card p-0 overflow-hidden relative group">
      {/* Background accents */}
      <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none transition-transform duration-700 group-hover:scale-110">
        <Target size={150} />
      </div>

      <div className="p-8 border-b border-white/[0.03] flex justify-between items-center relative z-10 bg-bg/50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-accent/10 text-accent">
            <Shield size={16} />
          </div>
          <h3 className="font-space text-lg font-bold tracking-tight uppercase">Personal Threat Profile</h3>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          <span className="font-mono text-[0.5rem] text-white uppercase tracking-widest">Live Analysis</span>
        </div>
      </div>

      <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
        <div className="space-y-6">
          <div className="space-y-2">
            <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Primary Threat Vector</div>
            <div className="flex items-center gap-3">
              <AlertTriangle className="text-danger" size={20} />
              <div className="font-space text-2xl font-black uppercase text-white">
                {insights.top_threat_type}
              </div>
            </div>
            <p className="font-mono text-[0.6rem] text-muted max-w-[200px] leading-relaxed">
              Based on your history, scammers are primarily targeting you via this vector.
            </p>
          </div>

          <div className="space-y-2">
             <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Highest Risk Period</div>
             <div className="flex items-center gap-3">
               <Clock className="text-warning" size={18} />
               <div className="font-space text-lg font-bold uppercase text-white">
                 {insights.highest_risk_period}
               </div>
             </div>
          </div>
        </div>

        <div className="flex flex-col justify-center space-y-6 border-l border-white/5 pl-8">
           <div className="flex justify-between items-end border-b border-white/5 pb-4">
             <div className="space-y-1">
               <div className="font-space text-sm font-bold uppercase text-white">Safety Score</div>
               <div className="font-mono text-[0.5rem] text-muted uppercase">System Evaluation</div>
             </div>
             <div className={`font-space text-3xl font-black ${insights.safety_score > 80 ? 'text-success' : insights.safety_score > 50 ? 'text-warning' : 'text-danger'}`}>
               {insights.safety_score}%
             </div>
           </div>

           <div className="flex justify-between items-end">
             <div className="space-y-1">
               <div className="font-space text-sm font-bold uppercase text-white">Scams Avoided</div>
               <div className="font-mono text-[0.5rem] text-muted uppercase">Total Intercepts</div>
             </div>
             <div className="font-space text-2xl font-bold text-accent">
               {insights.scams_avoided}
             </div>
           </div>
        </div>
      </div>
    </div>
  )
}
