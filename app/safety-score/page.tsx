'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { Activity, ShieldCheck, TrendingUp, TrendingDown, Info, ShieldAlert } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useAuth } from '@/backend/core/AuthProvider'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function SafetyScore() {
  const [mounted, setMounted] = useState(false)
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    setTimeout(() => setMounted(true), 0)
    async function fetchScoreHistory() {
      try {
        const token = localStorage.getItem('vsdp_token')
        if (!token) return

        // Also fetch current user profile to get the live score
        const meRes = await fetch('http://localhost:8000/api/users/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const meData = meRes.ok ? await meRes.json() : null

        const res = await fetch('http://localhost:8000/api/users/me/score-history', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          let data = await res.json()
          data.reverse() // Chronological order

          const formattedData = data.map((item: any) => {
            const date = new Date(item.recorded_at)
            return {
              date: `${date.getDate()}/${date.getMonth()+1}`,
              fullDate: date.toLocaleDateString(),
              score: Math.round(item.score * 10) / 10
            }
          })

          if (meData && meData.safety_score) {
             const today = new Date()
             formattedData.push({
                date: "Now",
                fullDate: today.toLocaleDateString(),
                score: Math.round(meData.safety_score * 10) / 10
             })
          }

          // if empty provide some mock data for visualization if user is new
          if (formattedData.length === 0 && meData) {
             formattedData.push({ date: "Start", score: 100 })
             formattedData.push({ date: "Now", score: Math.round(meData.safety_score * 10) / 10 })
          }

          setHistory(formattedData)
        }
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchScoreHistory()
  }, [])

  if (!mounted) return null

  const currentScore = history.length > 0 ? history[history.length - 1].score : 100
  const previousScore = history.length > 1 ? history[history.length - 2].score : currentScore
  const change = currentScore - previousScore
  const isUp = change >= 0

  return (
    <div className="flex min-h-screen bg-[#0b0b18] text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Safety Score & Gamification" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* Header Section */}
          <div className="flex flex-col gap-2">
             <h2 className="text-3xl font-space font-bold uppercase tracking-tight">Your Defense Profile</h2>
             <p className="text-[#94a3b8] font-mono text-xs uppercase tracking-widest">
               Track your proactive defense efforts and community contribution.
             </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
             {/* Score Card */}
             <motion.div
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               className="col-span-1 border border-[rgba(124,58,237,0.15)] bg-[#10101f]/60 rounded-xl p-8 relative overflow-hidden flex flex-col justify-center items-center"
             >
                <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                  <ShieldCheck size={120} />
                </div>

                <h3 className="font-mono text-sm uppercase tracking-widest text-[#94a3b8] mb-4">Current Safety Score</h3>
                <div className={`text-6xl font-space font-black tracking-tighter ${currentScore >= 90 ? 'text-[#7fff6e]' : currentScore >= 70 ? 'text-[#eab308]' : 'text-[#ef4444]'}`}>
                  {currentScore}
                </div>

                {change !== 0 && (
                  <div className={`mt-4 flex items-center gap-2 text-xs font-mono uppercase tracking-widest ${isUp ? 'text-[#7fff6e]' : 'text-[#ef4444]'}`}>
                    {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    <span>{Math.abs(change).toFixed(1)} pts since last update</span>
                  </div>
                )}
             </motion.div>

             {/* Info Cards */}
             <motion.div
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: 0.1 }}
               className="col-span-2 grid grid-cols-2 gap-6"
             >
                <div className="border border-[rgba(255,255,255,0.05)] bg-[rgba(255,255,255,0.01)] rounded-xl p-6 space-y-4">
                   <div className="flex items-center gap-3 text-[#c4b5fd]">
                      <Info size={18} />
                      <h4 className="font-space uppercase text-sm tracking-widest">How to earn points</h4>
                   </div>
                   <ul className="space-y-3 font-mono text-xs text-[#94a3b8] leading-relaxed">
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#7fff6e] rounded-full"></span> File official FIR reports</li>
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#7fff6e] rounded-full"></span> Participate in active Honeypot traps</li>
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#7fff6e] rounded-full"></span> Maintain a clean threat history (daily bonus)</li>
                   </ul>
                </div>

                <div className="border border-[rgba(255,255,255,0.05)] bg-[rgba(255,255,255,0.01)] rounded-xl p-6 space-y-4">
                   <div className="flex items-center gap-3 text-[#f87171]">
                      <ShieldAlert size={18} />
                      <h4 className="font-space uppercase text-sm tracking-widest">Score Penalties</h4>
                   </div>
                   <ul className="space-y-3 font-mono text-xs text-[#94a3b8] leading-relaxed">
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#ef4444] rounded-full"></span> Engaging with known scam numbers</li>
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#ef4444] rounded-full"></span> Submitting false reports</li>
                      <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#ef4444] rounded-full"></span> Bypassing system security warnings</li>
                   </ul>
                </div>
             </motion.div>
          </div>

          {/* Chart Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="border border-[rgba(124,58,237,0.15)] bg-[#10101f]/60 rounded-xl p-8"
          >
             <h3 className="font-space text-lg uppercase tracking-widest mb-8 border-b border-[rgba(255,255,255,0.05)] pb-4">Historical Progression</h3>

             {loading ? (
                <div className="h-64 flex items-center justify-center font-mono text-xs text-[#94a3b8] uppercase tracking-widest">
                  Loading telemetry...
                </div>
             ) : history.length > 0 ? (
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                      <XAxis
                        dataKey="date"
                        stroke="#475569"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        fontFamily="monospace"
                      />
                      <YAxis
                        domain={['dataMin - 5', 100]}
                        stroke="#475569"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        fontFamily="monospace"
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0b0b18',
                          border: '1px solid rgba(124,58,237,0.2)',
                          borderRadius: '8px',
                          fontFamily: 'monospace',
                          fontSize: '12px'
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#0b0b18' }}
                        activeDot={{ r: 6, fill: '#7fff6e', strokeWidth: 0 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
             ) : (
                <div className="h-64 flex items-center justify-center font-mono text-xs text-[#94a3b8] uppercase tracking-widest">
                  No historical data available yet.
                </div>
             )}
          </motion.div>

        </div>
      </main>
    </div>
  )
}
