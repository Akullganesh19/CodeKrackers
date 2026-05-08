'use client'

import { useState, useEffect } from 'react'
import { Bell, Volume2, VolumeX, X, ShieldAlert, MessageSquare } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function NotificationSettings({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [settings, setSettings] = useState({
    globalMuted: false,
    sessionExpiry: true,
    newNotification: true,
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setSettings({
        globalMuted: localStorage.getItem('vsdp_session_muted') === 'true',
        sessionExpiry: localStorage.getItem('vsdp_sound_session_expiry') !== 'false',
        newNotification: localStorage.getItem('vsdp_sound_new_notification') !== 'false',
      })
    }
  }, [isOpen])

  const updateSetting = (key: keyof typeof settings, value: boolean) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)
    
    if (typeof window !== 'undefined') {
      if (key === 'globalMuted') localStorage.setItem('vsdp_session_muted', String(value))
      if (key === 'sessionExpiry') localStorage.setItem('vsdp_sound_session_expiry', String(value))
      if (key === 'newNotification') localStorage.setItem('vsdp_sound_new_notification', String(value))
      
      // Dispatch storage event for other components to sync
      window.dispatchEvent(new Event('storage'))
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110]" 
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-obsidian border border-white/10 p-8 rounded-2xl shadow-2xl z-[120] space-y-8"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[#7c3aed]/10 text-[#a78bfa]">
                  <Bell size={20} />
                </div>
                <h2 className="font-space text-xl tracking-tight uppercase">Notification Grid</h2>
              </div>
              <button onClick={onClose} className="text-[#64748b] hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="space-y-6">
              {/* Global Mute */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-4">
                  <div className={settings.globalMuted ? "text-red-400" : "text-green-400"}>
                    {settings.globalMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                  </div>
                  <div>
                    <div className="font-mono text-[0.6rem] uppercase tracking-widest text-white">Global Audio Shield</div>
                    <div className="font-mono text-[0.5rem] uppercase text-[#64748b]">Mute all system alerts</div>
                  </div>
                </div>
                <button 
                  onClick={() => updateSetting('globalMuted', !settings.globalMuted)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${settings.globalMuted ? 'bg-red-500/20 border border-red-500/40' : 'bg-white/10 border border-white/10'}`}
                >
                  <motion.div 
                    animate={{ x: settings.globalMuted ? 26 : 4 }}
                    className={`absolute top-1 w-3.5 h-3.5 rounded-full ${settings.globalMuted ? 'bg-red-400' : 'bg-[#64748b]'}`}
                  />
                </button>
              </div>

              <div className="space-y-4 pt-2">
                <div className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-[0.4em] px-1">Specific Channels</div>
                
                {/* Session Expiry */}
                <div className="flex items-center justify-between px-1">
                  <div className="flex items-center gap-4">
                    <ShieldAlert size={18} className="text-[#a78bfa]/60" />
                    <div>
                      <div className="font-mono text-[0.6rem] uppercase text-white">Session Expiry</div>
                      <div className="font-mono text-[0.5rem] uppercase text-[#475569]">Expiry warning alerts</div>
                    </div>
                  </div>
                  <button 
                    onClick={() => updateSetting('sessionExpiry', !settings.sessionExpiry)}
                    className={`w-10 h-5 rounded-full transition-colors relative ${settings.sessionExpiry ? 'bg-[#7c3aed]/20 border border-[#7c3aed]/40' : 'bg-white/5 border border-white/5'}`}
                  >
                    <motion.div 
                      animate={{ x: settings.sessionExpiry ? 22 : 4 }}
                      className={`absolute top-0.5 w-3 h-3 rounded-full ${settings.sessionExpiry ? 'bg-[#a78bfa]' : 'bg-[#475569]'}`}
                    />
                  </button>
                </div>

                {/* New Notifications */}
                <div className="flex items-center justify-between px-1">
                  <div className="flex items-center gap-4">
                    <MessageSquare size={18} className="text-[#a78bfa]/60" />
                    <div>
                      <div className="font-mono text-[0.6rem] uppercase text-white">Threat Intel</div>
                      <div className="font-mono text-[0.5rem] uppercase text-[#475569]">New report notifications</div>
                    </div>
                  </div>
                  <button 
                    onClick={() => updateSetting('newNotification', !settings.newNotification)}
                    className={`w-10 h-5 rounded-full transition-colors relative ${settings.newNotification ? 'bg-[#7c3aed]/20 border border-[#7c3aed]/40' : 'bg-white/5 border border-white/5'}`}
                  >
                    <motion.div 
                      animate={{ x: settings.newNotification ? 22 : 4 }}
                      className={`absolute top-0.5 w-3 h-3 rounded-full ${settings.newNotification ? 'bg-[#a78bfa]' : 'bg-[#475569]'}`}
                    />
                  </button>
                </div>
              </div>
            </div>

            <div className="pt-4 text-center">
              <p className="font-mono text-[0.45rem] text-[#475569] uppercase tracking-widest">Preferences stored locally on this terminal</p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}