'use client'
import { phantomFetch } from '@/app/lib/fetch';


import React, { useState, useEffect } from 'react'
import { Shield, Zap, Globe, MessageSquare, Bot } from 'lucide-react'
import { motion } from 'framer-motion'

export default function OpenClawStatus() {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await phantomFetch('http://localhost:8000/api/openclaw/status')
        const data = await response.json()
        setStatus(data)
      } catch (error) {
        console.error("OpenClaw offline")
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
  }, [])

  if (loading) return null

  return (
    <div className="vsdp-card p-6 bg-accent/5 border-accent/20">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent/10 rounded-lg">
            <Globe className="text-accent" size={20} />
          </div>
          <div>
            <h3 className="font-space font-bold uppercase tracking-tight text-sm">OpenClaw Gateway</h3>
            <p className="font-mono text-[10px] text-muted uppercase">Multi-Channel AI Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status?.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="font-mono text-[10px] uppercase tracking-widest">{status?.status || 'Offline'}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <p className="font-mono text-[10px] text-muted uppercase tracking-tighter">Active Channels</p>
          <div className="flex gap-2">
            {status?.channels?.map((c: string) => (
              <div key={c} title={c} className="w-6 h-6 rounded bg-surface border border-white/5 flex items-center justify-center">
                <MessageSquare size={12} className="text-accent/60" />
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-1 text-right">
          <p className="font-mono text-[10px] text-muted uppercase tracking-tighter">AI Agents</p>
          <div className="flex items-center justify-end gap-2 text-accent">
            <Bot size={16} />
            <span className="font-space font-black">{status?.active_agents || 0}</span>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-white/5">
        <button className="w-full py-2 bg-accent/10 hover:bg-accent/20 border border-accent/30 rounded font-mono text-[10px] uppercase font-bold tracking-widest transition-all">
          Deploy New Agent [Thinking: High]
        </button>
      </div>
    </div>
  )
}
