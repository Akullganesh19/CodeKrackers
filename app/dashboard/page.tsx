'use client'

import { useAuth } from '@/backend/core/AuthProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { Shield, Building, User, Lock, Activity } from 'lucide-react'

/**
 * Sub-dashboard for Citizens
 */
const CitizenDashboard = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-space">Personal Defense Terminal</h1>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
        <Activity className="text-blue-400 mb-2" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-blue-400">My Reports</h3>
        <p className="text-3xl font-space mt-2">12 Active</p>
      </div>
      <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
        <Shield className="text-green-400 mb-2" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-green-400">Protection Status</h3>
        <p className="text-3xl font-space mt-2">Shield Active</p>
      </div>
    </div>
  </div>
)

/**
 * Sub-dashboard for Bank Officers
 */
const BankDashboard = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-space">Financial Integrity Portal</h1>
    <div className="p-6 bg-white/5 border border-white/10 rounded-xl border-l-4 border-l-yellow-500">
      <Building className="text-yellow-500 mb-2" />
      <h3 className="font-mono text-xs uppercase tracking-widest text-yellow-500">Pending Fraud Verifications</h3>
      <p className="text-4xl font-space mt-2">28 CASES</p>
    </div>
  </div>
)

/**
 * Sub-dashboard for Cyber Officers
 */
const OfficerDashboard = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-space">Investigation Command</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl">
        <Lock className="text-red-500 mb-2" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-red-500">Critical Threats</h3>
        <p className="text-3xl font-space mt-2">04</p>
      </div>
      {/* More investigation tools */}
    </div>
  </div>
)

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) return <div className="flex h-screen items-center justify-center font-mono text-xs animate-pulse">SYNCHRONIZING SECURE SESSION...</div>
  if (!user) return null

  const renderDashboard = () => {
    switch (user.role) {
      case 'bank':
        return <BankDashboard />
      case 'officer':
        return <OfficerDashboard />
      case 'admin':
      case 'superadmin':
        return <div className="p-10 border border-red-500/30 rounded-lg bg-red-500/5">System Administrator Access Granted</div>
      case 'citizen':
      default:
        return <CitizenDashboard />
    }
  }

  return (
    <div className="min-h-screen p-8 md:p-12 max-w-7xl mx-auto">
      <div className="mb-10 flex items-center justify-between border-b border-white/5 pb-8">
        <div className="font-mono text-[0.6rem] uppercase tracking-[0.4em] text-[#64748b]">
          Clearance Level: <span className="text-white">{user.role}</span>
        </div>
        <div className="font-mono text-[0.6rem] uppercase tracking-[0.4em] text-[#64748b]">
          Identity: <span className="text-white">{user.sub}</span>
        </div>
      </div>
      {renderDashboard()}
    </div>
  )
}