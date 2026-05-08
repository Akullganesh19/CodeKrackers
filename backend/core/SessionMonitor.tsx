'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { isTokenExpired, getTimeUntilTokenExpiry, logout, refreshToken } from '@/backend/core/auth-utils'; // Adjust path as needed
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Volume2, VolumeX } from 'lucide-react';

interface SessionMonitorLabels {
  title: string;
  expiringIn: string;
  minutesSuffix: string;
  dismiss: string;
  stayLoggedIn: string;
  refreshing: string;
  mute: string;
  unmute: string;
}

interface SessionMonitorProps {
  warningThresholdSeconds?: number; // Time in seconds before expiry to show the warning
  refreshIntervalSeconds?: number; // How often to check the session status in seconds
  labels?: Partial<SessionMonitorLabels>;
  soundEnabled?: boolean;
  soundUrl?: string;
}

export default function SessionMonitor({
  warningThresholdSeconds = 300, // Default to 5 minutes
  refreshIntervalSeconds = 30,   // Default to 30 seconds
  labels = {},
  soundEnabled = true,
  soundUrl = '/sounds/alert.mp3'
}: SessionMonitorProps) {
  const finalLabels: SessionMonitorLabels = {
    title: 'Session Expiring Soon!',
    expiringIn: 'Your session will expire in',
    minutesSuffix: 'minutes.',
    dismiss: 'Dismiss',
    stayLoggedIn: 'Stay Logged In',
    refreshing: 'Refreshing...',
    mute: 'Mute',
    unmute: 'Unmute',
    ...labels
  };

  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const originalTitle = useRef<string | null>(null);
  const [isExpirySoundEnabled, setIsExpirySoundEnabled] = useState(true)

  useEffect(() => {
    const syncSettings = () => {
      setIsExpirySoundEnabled(localStorage.getItem('vsdp_sound_session_expiry') !== 'false')
    }
    syncSettings()
    window.addEventListener('storage', syncSettings)
    return () => window.removeEventListener('storage', syncSettings)
  }, [])

  const [isMuted, setIsMuted] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('vsdp_session_muted') === 'true';
    }
    return false;
  });

  const toggleMute = () => {
    const newState = !isMuted;
    setIsMuted(newState);
    if (typeof window !== 'undefined') {
      localStorage.setItem('vsdp_session_muted', String(newState));
    }
  };

  const checkSession = useCallback(async () => {
    if (isTokenExpired()) {
      logout();
      return;
    }

    const remaining = getTimeUntilTokenExpiry();
    setTimeRemaining(remaining);

    if (remaining > 0 && remaining <= warningThresholdSeconds) {
      setShowWarning(true);
    } else {
      setShowWarning(false);
    }
  }, [warningThresholdSeconds]);

  const handleRefreshSession = useCallback(async () => {
    if (isRefreshing) return;
    setIsRefreshing(true);
    const success = await refreshToken();
    setIsRefreshing(false);
    if (success) {
      setShowWarning(false);
      checkSession(); // Re-check session to update expiry time
    } else {
      // refreshToken already calls logout on failure
    }
  }, [isRefreshing, checkSession]);

  useEffect(() => {
    // Initial check
    checkSession();

    // Dynamically adjust interval: 1s for smooth countdown if warning is active,
    // otherwise use the background refresh rate.
    const activeInterval = showWarning ? 1 : refreshIntervalSeconds;
    const intervalId = setInterval(checkSession, activeInterval * 1000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [checkSession, refreshIntervalSeconds, showWarning]);

  // Play notification sound when the warning is first displayed
  useEffect(() => {
    if (showWarning && soundEnabled && !isMuted && isExpirySoundEnabled && typeof window !== 'undefined') {
      const audio = new Audio(soundUrl);
      audio.play().catch(err => {
        console.warn('SessionMonitor: Audio playback failed. This is often due to browser autoplay policies.', err);
      });
    }
  }, [showWarning, soundEnabled, soundUrl, isMuted, isExpirySoundEnabled]);

  // Tab notification: Flash the page title when warning is active
  useEffect(() => {
    if (typeof window === 'undefined') return;

    if (!showWarning) {
      // Restore original title when warning is gone
      if (originalTitle.current) {
        document.title = originalTitle.current;
        originalTitle.current = null;
      }
      return;
    }

    // Store current title before we start changing it
    if (!originalTitle.current) {
      originalTitle.current = document.title;
    }

    const isCritical = timeRemaining <= 60;
    const alertTitle = isCritical ? '🛑 SESSION CRITICAL!' : '⚠️ SESSION EXPIRING...';
    let toggle = false;

    const intervalId = setInterval(() => {
      document.title = toggle ? alertTitle : (originalTitle.current || 'VSDP');
      toggle = !toggle;
    }, 1000);

    return () => clearInterval(intervalId);
  }, [showWarning, timeRemaining <= 60]); 
  // Only re-run when warning state changes or enters critical phase

  if (!showWarning) return null;

  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;

  const isCritical = timeRemaining <= 60;

  // Calculate percentage: (current / total) * 100
  const progress = Math.min(100, Math.max(0, (timeRemaining / warningThresholdSeconds) * 100));

  return (
    <AnimatePresence>
      {showWarning && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-8 right-8 bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] text-white p-6 rounded-lg shadow-lg max-w-sm z-50 border border-[#a78bfa]/30"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Sparkles size={20} className="text-white mr-2" />
              <h3 className="font-bold text-lg">{finalLabels.title}</h3>
            </div>
            {soundEnabled && (
              <button
                onClick={toggleMute}
                className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-white/70 hover:text-white"
                title={isMuted ? finalLabels.unmute : finalLabels.mute}
              >
                {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
              </button>
            )}
          </div>

          {/* Countdown Progress Bar */}
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
            <motion.div
              initial={{ width: '100%' }}
              animate={{ width: `${progress}%` }}
              transition={{ 
                duration: 1, 
                ease: 'linear' 
              }}
              className={`h-full transition-colors duration-500 ${
                isCritical 
                  ? 'bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_10px_rgba(220,38,38,0.5)]' 
                  : 'bg-gradient-to-r from-[#a78bfa] to-white'
              }`}
            />
          </div>

          <p className="text-sm mb-6">
            {finalLabels.expiringIn}{' '}
            <motion.span
              animate={isCritical ? { 
                scale: [1, 1.1, 1],
                opacity: [1, 0.8, 1]
              } : { 
                scale: 1,
                opacity: 1 
              }}
              transition={{ 
                duration: 1, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
              className={`font-mono font-bold inline-block transition-colors duration-500 ${
                isCritical ? 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]' : 'text-white'
              }`}
            >
              {minutes.toString().padStart(2, '0')}:{seconds.toString().padStart(2, '0')}
            </motion.span>{' '}
            {finalLabels.minutesSuffix}
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setShowWarning(false)}
              className="px-4 py-2 text-sm font-medium text-white rounded-md border border-white/20 hover:bg-white/10 transition-colors"
            >
              {finalLabels.dismiss}
            </button>
            <button
              onClick={handleRefreshSession}
              disabled={isRefreshing}
              className="px-4 py-2 text-sm font-medium bg-white text-[#7c3aed] rounded-md hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRefreshing ? finalLabels.refreshing : finalLabels.stayLoggedIn}
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}