'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/app/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Shield, ShieldAlert, Activity, Award } from 'lucide-react'

export default function MySafetyProfile() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchSafetyData() {
      try {
        const token = localStorage.getItem('vsdp_token')
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
        const res = await fetch(`${backendUrl}/api/users/me/safety`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (res.ok) {
          const json = await res.json()
          setData(json)
        }
      } catch (err) {
        console.error("Failed to fetch safety profile:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchSafetyData()
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen bg-bg text-white">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
        </main>
      </div>
    )
  }

  // Generate SVG path for the sparkline based on history
  const generateSparklinePath = () => {
    if (!data?.history || data.history.length === 0) {
      return "M 0 20 L 100 20"
    }
    const points = data.history.map((h: any, i: number) => {
      // Scale score 0-100 to y-axis 40-0
      const y = 40 - (h.score / 100) * 40
      const x = (i / Math.max(1, data.history.length - 1)) * 100
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    }).join(' ')
    return points
  }

  return (
    <div className="flex min-h-screen bg-bg text-white selection:bg-accent/20">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="My Safety Profile" />

        <div className="p-10 max-w-5xl mx-auto space-y-10">

          <div className="flex items-center gap-6 mb-8">
            <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center border border-accent/20">
              <Shield size={32} className="text-accent" />
            </div>
            <div>
              <h2 className="font-space text-3xl font-bold uppercase tracking-tight">Personal Security Posture</h2>
              <p className="font-mono text-sm text-muted uppercase tracking-widest mt-1">
                Your historical standing within the VSDP defense network
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="vsdp-card p-8 flex flex-col justify-between h-48">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="font-space text-5xl font-black text-accent">{data?.safety_score?.toFixed(1) || '100.0'}</div>
                  <div className="font-mono text-[0.6rem] text-muted uppercase tracking-[0.2em]">Safety Score</div>
                </div>
                <Activity size={20} className="text-accent/50" />
              </div>
              <div className="w-full h-10 mt-4 relative">
                 <svg className="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <motion.path
                      d={generateSparklinePath()}
                      fill="none"
                      stroke="#c4b5fd"
                      strokeWidth="2"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                    />
                 </svg>
              </div>
            </div>

            <div className="vsdp-card p-8 flex flex-col justify-between h-48 bg-gradient-to-br from-success/5 to-transparent border-success/20">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="font-space text-5xl font-black text-success">{data?.scams_avoided || 0}</div>
                  <div className="font-mono text-[0.6rem] text-success/70 uppercase tracking-[0.2em]">Scams Avoided</div>
                </div>
                <Award size={20} className="text-success/50" />
              </div>
              <div className="font-mono text-[0.65rem] text-muted leading-relaxed">
                Total number of verified fraudulent interactions you have successfully evaded with VSDP's help.
              </div>
            </div>

            <div className="vsdp-card p-8 flex flex-col justify-between h-48 bg-gradient-to-br from-warning/5 to-transparent border-warning/20">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="font-space text-5xl font-black text-warning">{data?.reported_threats || 0}</div>
                  <div className="font-mono text-[0.6rem] text-warning/70 uppercase tracking-[0.2em]">Threats Reported</div>
                </div>
                <ShieldAlert size={20} className="text-warning/50" />
              </div>
              <div className="font-mono text-[0.65rem] text-muted leading-relaxed">
                Your contributions to the national threat intelligence grid. Thank you for protecting the community.
              </div>
            </div>
          </div>

          <div className="vsdp-card p-8 space-y-6">
            <h3 className="font-space text-xl tracking-tight uppercase border-b border-white/5 pb-4">Recent Activity History</h3>

            {data?.history && data.history.length > 0 ? (
              <div className="space-y-4">
                {data.history.slice().reverse().map((record: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-white/[0.02] border border-white/5">
                    <div className="font-mono text-sm">Score Assessment</div>
                    <div className="flex items-center gap-6">
                      <span className="font-space text-lg font-bold">{record.score.toFixed(1)}</span>
                      <span className="font-mono text-[0.6rem] text-muted uppercase tracking-widest">
                        {record.date ? new Date(record.date).toLocaleDateString() : 'Unknown Date'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-10 text-center font-mono text-sm text-muted uppercase tracking-widest">
                No historical score data available yet.
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  )
}
