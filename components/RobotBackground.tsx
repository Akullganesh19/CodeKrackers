'use client'

import { useRef, useEffect, useState, Suspense } from 'react'
import RobotScene from '@/components/RobotScene'

export default function RobotBackground() {
  const cursorRef = useRef({ x: 0, y: 0 })
  const [mounted, setMounted] = useState(false)
  const [gesture, setGesture] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
    const onMove = (e: MouseEvent) => {
      cursorRef.current.x = (e.clientX / window.innerWidth  - 0.5) * 2
      cursorRef.current.y = (e.clientY / window.innerHeight - 0.5) * 2
    }

    const onGesture = (e: any) => {
      if (e.detail?.type) {
        setGesture(e.detail.type)
      } else {
        setGesture(null)
      }
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('vsdp-gesture', onGesture)
    
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('vsdp-gesture', onGesture)
    }
  }, [])

  if (!mounted) return null

  return (
    <div
      id="vsdp-robot-container"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        pointerEvents: 'none',
        background: 'radial-gradient(ellipse 60% 70% at 50% 55%, rgba(196,181,253,0.12) 0%, rgba(139,92,246,0.05) 40%, transparent 70%)',
      }}
    >
      <Suspense fallback={null}>
        <RobotScene cursorRef={cursorRef} gesture={gesture} />
      </Suspense>
    </div>
  )
}
