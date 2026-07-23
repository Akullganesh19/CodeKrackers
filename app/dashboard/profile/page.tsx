'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  User, Shield, Smartphone, AlertTriangle,
  CheckCircle2, Activity, ShieldAlert,
  Clock, MapPin
} from 'lucide-react'
import Topbar from '@/components/Topbar'


export default function ProfileDashboard() {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProfile() {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null

        // Ensure token exists to avoid unnecessary 401s if not logged in yet.
        if (!token) {
           setError("Authentication required.")
           setLoading(false)
           return
        }

        const res = await fetch('http://localhost:8000/api/users/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!res.ok) {
          throw new Error('Failed to load profile')
        }

        const data = await res.json()
        setProfile(data)
      } catch (err: any) {
        setError(err.message || 'An error occurred')
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [])

  if (loading) {
    return (
      <div className="flex-1 flex flex-col min-w-0 bg-obsidian text-text-primary min-h-screen items-center justify-center">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="flex-1 flex flex-col min-w-0 bg-obsidian text-text-primary min-h-screen p-8 items-center justify-center">
        <div className="vsdp-card p-8 border-danger/20 flex flex-col items-center max-w-md text-center gap-4">
          <AlertTriangle className="text-danger w-12 h-12" />
          <h2 className="font-space text-xl text-white">Error Loading Profile</h2>
          <p className="text-muted">{error || "Could not retrieve profile data."}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-obsidian text-text-primary min-h-screen overflow-y-auto">
      <Topbar title="My Profile & Activity" />

      <div className="p-8 max-w-6xl mx-auto w-full space-y-8">

        {/* HEADER SECTION */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 vsdp-card p-8 flex items-center gap-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 group-hover:bg-accent/10 transition-all duration-700" />

            <div className="w-24 h-24 rounded-full bg-accent/10 border border-accent/30 flex items-center justify-center shrink-0 shadow-[0_0_20px_rgba(124,58,237,0.15)] relative">
              <User className="w-10 h-10 text-accent" />
              {profile.role === 'citizen' ? null : (
                <div className="absolute -bottom-2 -right-2 bg-obsidian p-1 rounded-full border border-white/10">
                  <Shield className="w-4 h-4 text-warning" />
                </div>
              )}
            </div>

            <div className="space-y-2 z-10">
              <h2 className="font-space text-3xl font-bold text-white tracking-tight">
                {profile.full_name || "Unknown Citizen"}
              </h2>
              <div className="flex items-center gap-4 text-sm text-muted">
                <span className="font-mono bg-white/5 px-2 py-1 rounded border border-white/10">{profile.email}</span>
                <span className="capitalize px-2 py-1 rounded border border-white/10 flex items-center gap-1">
                  <Activity size={14} className="text-accent" />
                  {profile.role} Level
                </span>
              </div>
            </div>
          </div>

          <div className="vsdp-card p-8 flex flex-col justify-center items-center text-center relative overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-br from-success/10 to-transparent opacity-20" />
             <div className="relative z-10 space-y-2">
                <h3 className="font-space text-lg text-muted uppercase tracking-widest text-xs">Safety Score</h3>
                <div className="font-space text-5xl font-black text-success drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                  {profile.safety_score.toFixed(1)}
                </div>
                <p className="text-xs text-muted flex items-center justify-center gap-1 pt-2">
                  <CheckCircle2 size={12} className="text-success" />
                  {profile.scams_avoided} Scams Avoided
                </p>
             </div>
          </div>
        </div>

        {/* DETAILS GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* RECENT THREATS */}
          <div className="space-y-4">
            <h3 className="font-space text-sm text-white/80 uppercase tracking-widest flex items-center gap-2">
              <ShieldAlert size={16} className="text-warning" />
              Recent Scans & Intercepts
            </h3>

            <div className="vsdp-card p-0 overflow-hidden">
              {profile.recent_threats && profile.recent_threats.length > 0 ? (
                <div className="divide-y divide-white/5">
                  {profile.recent_threats.map((threat: any) => (
                    <div key={threat.id} className="p-4 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                      <div className="flex items-start gap-3">
                        <div className={`mt-1 w-2 h-2 rounded-full ${threat.severity === 'critical' ? 'bg-danger shadow-[0_0_8px_rgba(239,68,68,0.6)]' : threat.severity === 'high' ? 'bg-warning' : 'bg-success'}`} />
                        <div>
                          <div className="font-mono text-sm text-white group-hover:text-accent transition-colors">
                            {threat.source_number || "Unknown Source"}
                          </div>
                          <div className="text-xs text-muted flex items-center gap-2 mt-1">
                            <span className="uppercase">{threat.type}</span>
                            <span>•</span>
                            <span>{threat.status}</span>
                            <span>•</span>
                            <span className="flex items-center gap-1"><Clock size={10} /> {new Date(threat.detected_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-xs text-muted uppercase">Confidence</div>
                        <div className="font-space text-sm font-bold text-white">{(threat.confidence * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-muted border-t border-white/5">
                  <Shield className="w-8 h-8 mx-auto mb-3 opacity-20" />
                  <p className="font-mono text-xs uppercase">No recent threats detected</p>
                </div>
              )}
            </div>
          </div>

          {/* REGISTERED DEVICES */}
          <div className="space-y-4">
            <h3 className="font-space text-sm text-white/80 uppercase tracking-widest flex items-center gap-2">
              <Smartphone size={16} className="text-accent" />
              Active Devices
            </h3>

            <div className="vsdp-card p-0 overflow-hidden">
               {profile.devices && profile.devices.length > 0 ? (
                <div className="divide-y divide-white/5">
                  {profile.devices.map((device: any) => (
                    <div key={device.id} className="p-4 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white/40 group-hover:text-white transition-colors">
                          <Smartphone size={18} />
                        </div>
                        <div>
                          <div className="font-space text-sm text-white">{device.device}</div>
                          <div className="text-xs text-muted font-mono mt-0.5">{device.os}</div>
                        </div>
                      </div>
                      <div className="text-right text-xs text-muted space-y-1">
                        <div className="font-mono flex items-center justify-end gap-1"><MapPin size={10} /> {device.ip}</div>
                        <div>{new Date(device.registered_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
               ) : (
                <div className="p-12 text-center text-muted border-t border-white/5">
                  <Smartphone className="w-8 h-8 mx-auto mb-3 opacity-20" />
                  <p className="font-mono text-xs uppercase">No devices registered</p>
                </div>
               )}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
