'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/backend/core/AuthProvider'
import { motion } from 'framer-motion'
import NotificationSettings from '@/app/components/NotificationSettings'
import { 
  LayoutDashboard, 
  ShieldAlert, 
  FileText, 
  Users, 
  Settings, 
  Search,
  Lock,
  LogOut,
  Bell
} from 'lucide-react'

const navItems = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard, roles: ['citizen', 'bank', 'officer', 'admin', 'superadmin'] },
  { name: 'My Profile', href: '/dashboard/profile', icon: Users, roles: ['citizen', 'bank', 'officer', 'admin', 'superadmin'] },
  { name: 'Report Threat', href: '/dashboard/report', icon: ShieldAlert, roles: ['citizen', 'bank', 'officer', 'admin', 'superadmin'] },
  { name: 'Fraud Verification', href: '/dashboard/verification', icon: Search, roles: ['bank', 'officer', 'admin', 'superadmin'] },
  { name: 'Investigation', href: '/dashboard/investigation', icon: Lock, roles: ['officer', 'admin', 'superadmin'] },
  { name: 'FIR Management', href: '/dashboard/firs', icon: FileText, roles: ['officer', 'admin', 'superadmin'] },
  { name: 'User Management', href: '/dashboard/users', icon: Users, roles: ['admin', 'superadmin'] },
  { name: 'System Settings', href: '/dashboard/settings', icon: Settings, roles: ['superadmin'] },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const [notifications, setNotifications] = useState<Record<string, number>>({
    '/dashboard/report': 0,
  })
  const pathnameRef = useRef(pathname)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isMuted, setIsMuted] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('vsdp_session_muted') === 'true'
    }
    return false
  })
  const isMutedRef = useRef(isMuted)

  // Keep current pathname in a ref so the WebSocket handler can access it
  // without needing to restart the connection on every navigation.
  useEffect(() => {
    pathnameRef.current = pathname
  }, [pathname])

  // Sync mute state and maintain a ref to prevent stale closures in the WebSocket handler
  useEffect(() => {
    isMutedRef.current = isMuted
    const syncMute = () => {
      const muted = localStorage.getItem('vsdp_session_muted') === 'true'
      setIsMuted(muted)
      isMutedRef.current = muted
    }
    window.addEventListener('storage', syncMute)
    return () => window.removeEventListener('storage', syncMute)
  }, [isMuted])

  // Real-time WebSocket connection for notifications
  useEffect(() => {
    if (!user) return

    let socket: WebSocket | null = null
    let reconnectTimeout: NodeJS.Timeout

    const connect = () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : null
      const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
      const wsUrl = `${wsBaseUrl}/ws/threats?token=${token}`
      
      socket = new WebSocket(wsUrl)

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.route && data.route !== pathnameRef.current) {
            setNotifications(prev => ({
              ...prev,
              [data.route]: (prev[data.route] || 0) + (data.count || 1)
            }))

            const isNotifyEnabled = localStorage.getItem('vsdp_sound_new_notification') !== 'false'
            if (!isMutedRef.current && isNotifyEnabled) {
              const audio = new Audio('/sounds/notification.mp3')
              audio.play().catch(() => {})
            }
          }
        } catch (err) {
          console.error("Failed to parse notification message:", err)
        }
      }

      socket.onerror = (err) => {
        console.error("WebSocket connection error:", err)
      }

      socket.onclose = () => {
        // Attempt to reconnect after 5 seconds if the session is still active
        reconnectTimeout = setTimeout(connect, 5000)
      }
    }

    connect()

    // Cleanup: Terminate connection on unmount
    return () => {
      if (socket) {
        socket.close()
      }
      clearTimeout(reconnectTimeout)
    }
  }, [user])

  // Auto-clear notifications when the user visits the route
  useEffect(() => {
    if (notifications[pathname] > 0) {
      setNotifications(prev => ({
        ...prev,
        [pathname]: 0
      }))
      // Optional: Add a fetch() call here to notify the backend to persist the "read" state
    }
  }, [pathname, notifications])

  if (!user) return null

  // Filter navigation items based on the current user's role
  const filteredNavItems = navItems.filter(item => 
    item.roles.includes(user.role)
  )

  return (
    <div className="w-64 bg-obsidian border-r border-white/5 h-screen flex flex-col p-6 space-y-8 sticky top-0">
      <div className="flex items-center gap-3 px-2">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] flex items-center justify-center">
          <span className="text-white font-bold text-xs">◈</span>
        </div>
        <span className="font-space font-bold text-lg text-white">VSDP</span>
      </div>

      <nav className="flex-1 space-y-2">
        {filteredNavItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg font-mono text-[0.6rem] uppercase tracking-[0.2em] transition-all ${
                isActive 
                  ? 'bg-[#7c3aed]/10 border border-[#7c3aed]/30 text-[#a78bfa]' 
                  : 'text-[#64748b] hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon size={16} />
              <span>{item.name}</span>

              {notifications[item.href] > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="ml-auto flex h-4 w-4 items-center justify-center rounded-full bg-[#ff2056] text-[0.45rem] font-bold text-white shadow-[0_0_10px_rgba(255,32,86,0.3)] animate-pulse"
                >
                  {notifications[item.href]}
                </motion.span>
              )}
            </Link>
          )
        })}
      </nav>

      <div className="pt-6 border-t border-white/5 space-y-2">
        <button 
          onClick={() => setIsSettingsOpen(true)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-mono text-[0.6rem] uppercase tracking-[0.2em] text-[#64748b] hover:text-white transition-colors"
        >
          <Bell size={16} />
          <span>Alert Config</span>
        </button>
        <button 
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-mono text-[0.6rem] uppercase tracking-[0.2em] text-[#64748b] hover:text-red-400 transition-colors"
        >
          <LogOut size={16} />
          <span>Terminate Session</span>
        </button>
      </div>

      <NotificationSettings isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  )
}