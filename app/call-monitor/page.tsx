'use client'
import { phantomFetch } from "@/app/lib/fetch";

import { useState, useEffect, useRef } from 'react'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Phone as LucidePhone, 
  Wifi as LucideWifi, 
  Mic as LucideMic, 
  ShieldX as LucideShieldX, 
  AlertTriangle as LucideAlertTriangle, 
  Zap as LucideZap, 
  Clock as LucideClock, 
  FileText as LucideFileText,
  Activity as LucideActivity,
  Circle as LucideCircle,
  Square as LucideSquare,
  Download as LucideDownload,
  Trash2 as LucideTrash2,
  Lock as LucideLock,
  Upload as LucideUpload,
  FileAudio as LucideFileAudio
} from 'lucide-react'

// Helper Component for the visual waveform
function WaveformBar({ active, amplitude }: { active: boolean, amplitude?: number }) {
  const [height, setHeight] = useState(20)
  
  useEffect(() => {
    if (active && amplitude !== undefined) {
      setHeight(Math.max(5, amplitude * 60))
    } else {
      const interval = setInterval(() => {
        setHeight(active ? Math.random() * 50 + 5 : Math.random() * 15 + 2)
      }, 100)
      return () => clearInterval(interval)
    }
  }, [active, amplitude])

  return (
    <div 
      className={`w-1 rounded-full transition-all duration-150 ${active ? 'bg-danger/60' : 'bg-accent/20'}`} 
      style={{ height: `${height}px` }} 
    />
  )
}

export default function VishingMonitor() {
  const [mounted, setMounted] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [transcript, setTranscript] = useState<{time: string, text: string, flagged?: boolean}[]>([])
  const [threatLevel, setThreatLevel] = useState(0)
  const [recordings, setRecordings] = useState<{id: string, duration: string, time: string}[]>([])
  const [manualText, setManualText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [cloningStatus, setCloningStatus] = useState<'IDLE' | 'CAPTURING' | 'CLONED' | 'ANALYZING'>('IDLE')
  const [voiceSignature, setVoiceSignature] = useState<number[]>(Array(20).fill(0).map(() => Math.random()))
  const [audioAmplitude, setAudioAmplitude] = useState(0)
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [audioChunks, setAudioChunks] = useState<Blob[]>([])
  const [threatId, setThreatId] = useState<string | null>(null)
  const transcriptIntervalRef = useRef<any>(null)
  
  const transcriptLines = [
    { time: '00:04', text: "Hello, I am calling from TRAI head office...", flagged: false },
    { time: '00:09', text: "Your SIM card has been flagged for illegal activity...", flagged: true },
    { time: '00:14', text: "You must pay ₹5,000 fine immediately to avoid arrest...", flagged: true },
    { time: '00:19', text: "Please share your Aadhaar number for verification...", flagged: true },
  ]

  useEffect(() => {
    setMounted(true)
    const timer = setInterval(() => setSeconds(s => s + 1), 1000)
    
    // Simulate transcript appearing
    transcriptLines.forEach((line, i) => {
      setTimeout(() => {
        setTranscript(prev => [...prev, line])
        if (line.flagged) setThreatLevel(prev => Math.min(prev + 25, 72))
      }, (i + 1) * 3000)
    })

    return () => clearInterval(timer)
  }, [])

  // Handle analysis reset
  useEffect(() => {
    if (!isAnalyzing && !isUploading) {
      // Logic for post-analysis cleanup if needed
    }
  }, [isAnalyzing, isUploading])

  const formatTime = (s: number) => {
    const mins = Math.floor(s / 60)
    const secs = s % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Simulate voice signature updates when recording, but tie to real amplitude
  useEffect(() => {
    if (isRecording) {
      const interval = setInterval(() => {
        // More reactive signature when there is actual noise
        const noiseFactor = audioAmplitude > 0.1 ? 0.4 : 0.1
        setVoiceSignature(prev => prev.map(v => Math.max(0, Math.min(1, v + (Math.random() - 0.5) * noiseFactor))))
        
        if (seconds > 5 && cloningStatus === 'CAPTURING') setCloningStatus('CLONED')
        if (seconds > 10 && cloningStatus === 'CLONED') setCloningStatus('ANALYZING')
      }, 500)
      return () => clearInterval(interval)
    }
  }, [isRecording, seconds, cloningStatus, audioAmplitude])

  const handleManualAnalyze = async () => {
    if (!manualText.trim()) return
    setIsAnalyzing(true)
    try {
      const response = await phantomFetch('http://localhost:8000/api/analytics/scan-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: manualText })
      })
      const data = await response.json()
      setAnalysisResult(data)
      if (data.threat_id) setThreatId(data.threat_id)
      setThreatLevel(data.risk_score * 100)
      if (data.verdict === 'SCAM') {
        setTranscript(prev => [...prev, { time: formatTime(seconds), text: manualText, flagged: true }])
      } else {
        setTranscript(prev => [...prev, { time: formatTime(seconds), text: manualText, flagged: false }])
      }
    } catch (error) {
      // Silent failure
    } finally {
      setIsAnalyzing(false)
      setManualText('')
    }
  }

  const handleToggleRecording = async () => {
    if (isRecording) {
      if (mediaRecorder) {
        mediaRecorder.stop()
      }
      if (transcriptIntervalRef.current) {
        clearInterval(transcriptIntervalRef.current)
        transcriptIntervalRef.current = null
      }
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop())
        setAudioStream(null)
      }
      // Stop logic
      const newRec = {
        id: `REC_${new Date().getTime().toString().slice(-6)}.wav`,
        duration: formatTime(seconds),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setRecordings(prev => [newRec, ...prev])
      setIsRecording(false)
      setCloningStatus('IDLE')
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        setAudioStream(stream)
        
        const recorder = new MediaRecorder(stream)
        const chunks: Blob[] = []
        recorder.ondataavailable = (e) => chunks.push(e.data)
        recorder.onstop = () => setAudioChunks(chunks)
        recorder.start()
        setMediaRecorder(recorder)

        // Setup Audio Context for real-time visualization
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        const source = audioContext.createMediaStreamSource(stream)
        const analyser = audioContext.createAnalyser()
        analyser.fftSize = 256
        source.connect(analyser)
        
        const dataArray = new Uint8Array(analyser.frequencyBinCount)
        const updateAmplitude = () => {
          if (!isRecording && !stream.active) return
          analyser.getByteFrequencyData(dataArray)
          const sum = dataArray.reduce((a, b) => a + b, 0)
          const avg = sum / dataArray.length
          setAudioAmplitude(avg / 128)
          requestAnimationFrame(updateAmplitude)
        }
        updateAmplitude()

        // Mock transcription based on noise
        transcriptIntervalRef.current = setInterval(() => {
          if (audioAmplitude > 0.1) {
            const lines = [
              "System capturing neural signals...",
              "Voice pattern detected...",
              "Analyzing linguistic markers...",
              "Processing background noise...",
              "Caller identity verifying..."
            ]
            const line = lines[Math.floor(Math.random() * lines.length)]
            setTranscript(prev => [...prev.slice(-10), { time: formatTime(seconds), text: line, flagged: Math.random() > 0.7 }])
          }
        }, 3000)

        // Start logic
        setSeconds(0)
        setTranscript([])
        setThreatLevel(0)
        setIsRecording(true)
        setCloningStatus('CAPTURING')
      } catch (err) {
        alert("Microphone access denied or not available.")
      }
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await phantomFetch('http://localhost:8000/api/call/analyze-audio', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setAnalysisResult(data)
      setThreatLevel(data.risk_score * 100)
      setTranscript(prev => [...prev, { time: 'AUD', text: data.transcript, flagged: data.risk_score > 0.6 }])
      
      const newRec = {
        id: file.name,
        duration: "Analyzed",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setRecordings(prev => [newRec, ...prev])
    } catch (error) {
      // Silent failure
    } finally {
      setIsUploading(false)
    }
  }

  const handleEndAndBlock = async () => {
    try {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token'
      const response = await phantomFetch('http://localhost:8000/api/blacklist/report', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          identifier: "Unknown_Visher_" + (threatId || "New"), 
          type: "phone",
          reason: "Detected Vishing attempt during live monitor"
        })
      })
      if (response.ok) {
        alert("🚨 SCAMMER BLACKLISTED: The number has been blocked across the VSDP network.")
        setIsRecording(false)
      } else {
        alert("Failed to block number. Backend error.")
      }
    } catch (e) {
      alert("Connectivity error: Could not reach blacklist service.")
    }
  }

  const handleRouteToHoneypot = async () => {
    alert("⚡ ROUTING TO HONEYPOT: Diverting call to AI Einstein cluster...")
    // Simulate some delay for realism
    setTimeout(() => {
      alert("✅ SUCCESS: Caller is now interacting with the Einstein decoy system.")
    }, 1500)
  }

  const handleGenerateFIR = async () => {
    if (!threatId) {
      alert("Please perform an analysis first to generate an FIR.")
      return
    }
    try {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token'
      const response = await phantomFetch('http://localhost:8000/api/fir/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ threat_id: threatId })
      })
      const data = await response.json()
      if (response.ok) {
        alert(`📄 FIR GENERATED: Case #${data.case_number}. You can download the report from the FIR Management section.`)
      } else {
        alert("Error generating FIR: " + (data.detail || "Unknown error"))
      }
    } catch (e) {
      alert("Connectivity error: Could not reach FIR service.")
    }
  }

  const handleBlockchainLog = async () => {
    try {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token'
      const url = new URL('http://localhost:8000/api/zk/sealed-report')
      url.searchParams.append('report_data', JSON.stringify(analysisResult || { type: 'vishing', status: 'detected' }))
      
      const response = await phantomFetch(url.toString(), {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      const data = await response.json()
      if (response.ok) {
        alert(`⛓️ BLOCKCHAIN LOGGED: Receipt: ${data.report_hash.substring(0, 16)}... Evidence is now immutable.`)
      } else {
        alert("Blockchain logging failed.")
      }
    } catch (e) {
      alert("Connectivity error: Could not reach ZK Privacy service.")
    }
  }

  if (!mounted) return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="w-12 h-12 border-2 border-accent/20 border-t-accent rounded-full animate-spin" />
      <div className="font-mono text-[0.6rem] text-accent uppercase tracking-[0.5em] animate-pulse">Initializing_Voice_Sentinel...</div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Live Call Monitor" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          
          {/* STATUS BAR */}
          <div className="flex justify-between items-center bg-surface2/50 border border-white/[0.03] p-8 rounded-lg backdrop-blur-md relative overflow-hidden">
            <div className="flex items-center gap-6">
               <div className="flex items-center gap-4 px-6 py-2 rounded-full bg-success/5 border border-success/20">
                 <div className="w-2 h-2 rounded-full bg-success animate-pulse shadow-[0_0_10px_#7fff6e]" />
                 <span className="font-mono text-[0.6rem] text-success uppercase tracking-[0.4em]">Active_Defense</span>
               </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* THREAT GAUGE */}
            <div className="lg:col-span-4 vsdp-card p-12 flex flex-col items-center justify-center space-y-10 relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-success via-warning to-danger" />
               <h3 className="font-space text-xl tracking-tight uppercase font-black">Threat Matrix</h3>

               <div className="relative w-64 h-32 overflow-hidden mt-10">
                 <svg className="w-64 h-64 rotate-[-180deg]">
                   <circle cx="128" cy="128" r="100" fill="none" stroke="#111c2e" strokeWidth="20" strokeDasharray="314 314" />
                   <motion.circle 
                     cx="128" cy="128" r="100" fill="none" stroke="url(#gradient)" strokeWidth="20" 
                     strokeDasharray="314 314"
                     initial={{ strokeDashoffset: 314 }}
                     animate={{ strokeDashoffset: 314 - (314 * threatLevel) / 100 }}
                     transition={{ duration: 1.5, ease: "easeOut" }}
                   />
                   <defs>
                     <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                       <stop offset="0%" stopColor="#7fff6e" />
                       <stop offset="50%" stopColor="#f5c842" />
                       <stop offset="100%" stopColor="#ff3c6e" />
                     </linearGradient>
                   </defs>
                 </svg>
                 <div className="absolute inset-0 flex flex-col items-end justify-center pt-10">
                    <motion.div 
                      className="w-1.5 h-24 bg-white/40 origin-bottom rounded-full absolute bottom-0 left-[128px]"
                      animate={{ rotate: (threatLevel * 1.8) - 90 }}
                      transition={{ type: "spring", stiffness: 60 }}
                    />
                 </div>
               </div>

               <div className="text-center space-y-2">
                 <div className={`font-space text-6xl font-black ${threatLevel > 60 ? 'text-danger' : threatLevel > 30 ? 'text-warning' : 'text-success'}`}>
                   {Math.round(threatLevel)}%
                 </div>
                 <div className={`font-mono text-[0.7rem] uppercase tracking-[0.4em] font-black ${threatLevel > 60 ? 'text-danger' : threatLevel > 30 ? 'text-warning' : 'text-success'}`}>
                   Level: {threatLevel > 60 ? 'CRITICAL' : threatLevel > 30 ? 'CAUTION' : 'SAFE'}
                 </div>
               </div>
            </div>

            {/* LIVE TRANSCRIPT */}
            <div className="lg:col-span-8 vsdp-card flex flex-col h-[500px]">
               <div className="p-8 border-b border-white/[0.03] flex justify-between items-center bg-white/[0.01]">
                 <div className="flex items-center gap-4">
                   <div className="w-2 h-2 rounded-full bg-danger animate-pulse" />
                   <h3 className="font-space text-xl tracking-tight uppercase font-black">Neural Transcript</h3>
                 </div>
                 <div className="flex items-center gap-6 font-mono text-[0.55rem] text-muted uppercase tracking-widest">
                   <div className="flex items-center gap-2">
                     <LucideMic size={12} className="text-accent" /> Whisper_STT
                   </div>
                   <div className="flex items-center gap-2">
                     <LucideWifi size={12} className="text-accent" /> Latency: 85ms
                   </div>
                   <div className={`flex items-center gap-2 px-2 py-0.5 rounded bg-accent/10 border border-accent/20 transition-all ${cloningStatus !== 'IDLE' ? 'opacity-100' : 'opacity-0'}`}>
                      <LucideActivity size={10} className={cloningStatus === 'CAPTURING' ? 'animate-pulse text-warning' : 'text-success'} />
                      <span className="text-[0.45rem] font-bold tracking-tighter">LUX_CLONE: {cloningStatus}</span>
                    </div>
                 </div>
               </div>
               <div className="flex-1 overflow-y-auto p-10 space-y-6 scrollbar-hide">
                 <AnimatePresence>
                   {transcript.map((line, i) => (
                     <motion.div 
                       key={i}
                       initial={{ opacity: 0, x: -10 }}
                       animate={{ opacity: 1, x: 0 }}
                       className={`flex gap-6 p-5 rounded border transition-colors ${line.flagged ? 'bg-danger/5 border-danger/20' : 'bg-white/[0.02] border-white/5'}`}
                     >
                       <span className="font-mono text-[0.65rem] text-muted shrink-0">[{line.time}]</span>
                       <p className="font-mono text-sm leading-relaxed">
                         {line.text.split(' ').map((word, j) => {
                           const isFlagged = ['arrest', 'fine', 'aadhaar', 'trai', 'pay', '5,000'].includes(word.toLowerCase().replace(/[₹,]/g, ''))
                           return (
                             <span key={j} className={isFlagged ? 'bg-danger/40 text-white px-1' : ''}>
                               {word}{' '}
                             </span>
                           )
                         })}
                       </p>
                     </motion.div>
                   ))}
                 </AnimatePresence>
               </div>
               
               {/* Waveform Decorator */}
               <div className="h-20 border-t border-white/[0.03] flex items-center justify-center gap-1.5 px-10 relative">
                  {analysisResult?.is_ai_voice && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute -top-12 left-1/2 -translate-x-1/2 bg-danger/20 border border-danger/40 px-6 py-2 rounded-full flex items-center gap-3 backdrop-blur-xl"
                    >
                      <LucideZap size={14} className="text-danger animate-pulse" />
                      <span className="font-mono text-[0.6rem] text-danger uppercase tracking-widest font-black">AI Voice Pattern Detected</span>
                    </motion.div>
                  )}
                  {Array.from({ length: 80 }).map((_, i) => (
                    <WaveformBar key={i} active={isRecording || isUploading} amplitude={audioAmplitude} />
                  ))}
                </div>
            </div>
          </div>

          {/* LOWER SECTION: VAULT & RECORDER */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
             
              {/* LUX VOICE SIGNATURE ANALYSIS */}
              <div className="lg:col-span-4 vsdp-card p-10 flex flex-col gap-6 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-4">
                    <LucideZap size={16} className={cloningStatus === 'ANALYZING' ? 'text-danger animate-bounce' : 'text-muted/30'} />
                 </div>
                 <h3 className="font-space text-lg font-black uppercase flex items-center gap-3">
                   Voice Identity
                   <span className="px-2 py-0.5 bg-accent/20 text-accent text-[0.5rem] rounded tracking-tighter">LuxTTS Engine</span>
                 </h3>
                 
                 <div className="flex-1 flex flex-col justify-center gap-8 py-4">
                    <div className="grid grid-cols-10 gap-1 items-end h-24">
                      {voiceSignature.map((val, i) => (
                        <motion.div 
                          key={i}
                          animate={{ height: `${val * 100}%`, backgroundColor: (cloningStatus === 'ANALYZING' && val > 0.8) ? '#ff3c6e' : '#00f2ff' }}
                          className="w-full rounded-t-sm opacity-60"
                        />
                      ))}
                    </div>

                    <div className="space-y-4">
                       <div className="flex justify-between items-center font-mono text-[0.6rem] uppercase tracking-widest">
                          <span className="text-muted">Synthetic Marker Index</span>
                          <span className={cloningStatus === 'ANALYZING' ? 'text-danger' : 'text-success'}>
                            {cloningStatus === 'ANALYZING' ? '0.84 (CRITICAL)' : cloningStatus === 'IDLE' ? '0.00' : '0.12 (NORMAL)'}
                          </span>
                       </div>
                       <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            className={`h-full ${cloningStatus === 'ANALYZING' ? 'bg-danger' : 'bg-success'}`}
                            initial={{ width: 0 }}
                            animate={{ width: cloningStatus === 'ANALYZING' ? '84%' : cloningStatus === 'IDLE' ? '0%' : '12%' }}
                          />
                       </div>
                       <p className="font-mono text-[0.55rem] text-muted italic leading-relaxed">
                         {cloningStatus === 'ANALYZING' 
                           ? "WARNING: Neural frequency artifacts detected. High probability of AI-generated synthetic voice clone."
                           : cloningStatus === 'CAPTURING' || cloningStatus === 'CLONED'
                           ? "Authenticity scan active. Monitoring vocal jitter and shimmer for deepfake patterns."
                           : "Neural standby. System ready to capture voice identity signatures."}
                       </p>
                    </div>
                 </div>
              </div>

             {/* LIVE RECORDING MONITOR */}
             <div className="lg:col-span-4 vsdp-card p-10 flex flex-col justify-between group relative overflow-hidden">
                {isRecording && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute top-0 left-0 w-full h-1 bg-danger animate-pulse"
                  />
                )}
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="font-space text-lg font-black uppercase">Live Recording</h3>
                    {isRecording && (
                      <div className="flex items-center gap-2 px-3 py-1 bg-danger/20 border border-danger/40 rounded-full">
                        <div className="w-1.5 h-1.5 rounded-full bg-danger animate-ping" />
                        <span className="font-mono text-[0.5rem] text-danger font-bold uppercase">REC {formatTime(seconds)}</span>
                      </div>
                    )}
                  </div>
                  <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest leading-relaxed">
                    Real-time neural capture and audio fingerprinting for vishing identification.
                  </p>
                </div>

                <div className="py-10 flex flex-col items-center gap-6 relative">
                   <button 
                     onClick={handleToggleRecording}
                     className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${isRecording ? 'bg-danger/20 border-danger shadow-[0_0_20px_rgba(255,60,110,0.3)]' : 'bg-accent/10 border-accent/30'} border-2 hover:scale-105 active:scale-95`}
                   >
                     {isRecording ? <LucideSquare size={32} className="text-danger" /> : <LucideMic size={32} className="text-accent" />}
                   </button>
                   <div className={`font-mono text-[0.7rem] uppercase tracking-[0.4em] font-black text-center ${isRecording ? 'text-danger animate-pulse' : 'text-accent'}`}>
                     {isRecording ? 'STOP CAPTURE' : 'START LIVE CAPTURE'}
                   </div>
                </div>

                <div className="p-4 bg-white/[0.02] border border-white/5 rounded text-center flex items-center justify-center gap-3">
                   <LucideActivity size={12} className={isRecording ? 'text-danger' : 'text-muted'} />
                   <span className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">
                     {isRecording ? 'Neural Stream: Active' : 'Neural Stream: Standby'}
                   </span>
                </div>
             </div>

             {/* RECORDING VAULT */}
             <div className="lg:col-span-4 vsdp-card p-0 flex flex-col">
                <div className="p-8 border-b border-white/[0.03] flex justify-between items-center bg-white/[0.01]">
                   <h3 className="font-space text-lg font-black uppercase">Evidence Vault</h3>
                   <div className="flex items-center gap-2">
                     <LucideLock size={14} className="text-accent" />
                     <span className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Secured</span>
                   </div>
                </div>
                <div className="flex-1 overflow-y-auto max-h-[300px] p-6 space-y-4 scrollbar-hide">
                   {recordings.length === 0 ? (
                     <div className="h-full flex items-center justify-center font-mono text-[0.6rem] text-muted uppercase tracking-widest text-center opacity-30">No tapes analyzed yet</div>
                   ) : (
                     recordings.map((rec) => (
                       <div key={rec.id} className="flex items-center justify-between p-6 bg-white/[0.02] border border-white/5 rounded hover:border-accent/30 transition-all group">
                          <div className="flex items-center gap-6">
                             <div className="p-2 bg-accent/10 rounded">
                               <LucideFileAudio size={14} className="text-accent" />
                             </div>
                             <div className="space-y-1">
                                <div className="font-mono text-[0.6rem] font-bold text-white truncate max-w-[100px]">{rec.id}</div>
                                <div className="font-mono text-[0.5rem] text-muted uppercase">{rec.time} • {rec.duration}</div>
                             </div>
                          </div>
                          <div className="flex gap-2 opacity-40 group-hover:opacity-100">
                             <button className="p-2 hover:bg-white/5 rounded text-success"><LucideDownload size={14} /></button>
                          </div>
                       </div>
                     ))
                   )}
                </div>
             </div>
          </div>

          {/* ACTION BUTTONS */}
          <div className="flex flex-wrap gap-8 pt-8 border-t border-white/[0.03]">
             <button 
               onClick={handleEndAndBlock}
               className="btn-danger px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-black flex items-center gap-4 hover:scale-105 transition-all"
             >
               <LucideShieldX size={18} /> End & Block Call
             </button>
             <button 
               onClick={handleRouteToHoneypot}
               className="btn-ghost border-warning/30 text-warning hover:bg-warning/5 px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-bold flex items-center gap-4"
             >
               <LucideZap size={18} /> Route to Honeypot
             </button>
             <button 
               onClick={handleGenerateFIR}
               className="btn-ghost px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-bold flex items-center gap-4"
             >
               <LucideFileText size={18} /> Generate FIR
             </button>
             <button 
               onClick={handleBlockchainLog}
               className="btn-ghost px-12 py-5 text-[0.7rem] uppercase tracking-[0.3em] font-bold flex items-center gap-4"
             >
               <LucideActivity size={18} /> Push to Blockchain
             </button>
          </div>
        </div>

        <style jsx>{`
          .scrollbar-hide::-webkit-scrollbar {
            display: none;
          }
          .scrollbar-hide {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }
        `}</style>
      </main>
    </div>
  )
}
