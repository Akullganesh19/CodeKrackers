'use client'

import { useRef, useMemo, useState, useEffect, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshDistortMaterial, MeshWobbleMaterial, ContactShadows, Environment } from '@react-three/drei'
import * as THREE from 'three'

/* ──────────────────────────────────────────────
   SPRING PHYSICS — realistic overshoot + settle
────────────────────────────────────────────── */
type Spring = { value: number; vel: number }

function springStep(s: Spring, target: number, stiffness: number, damping: number, dt: number) {
  const force = stiffness * (target - s.value) - damping * s.vel
  s.vel += force * dt
  s.value += s.vel * dt
}

/* ─── TARGET SMOOTHING ─── */
function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t
}

/* ──────────────────────────────────────────────
   MATERIALS — Premium Apple-style palette
────────────────────────────────────────────── */
const M = {
  hull:    { color: '#050a1a', metalness: 0.95, roughness: 0.1  }, // Deep Navy Black
  panel:   { color: '#0a1428', metalness: 0.85, roughness: 0.15 }, // Slightly lighter navy
  accent:  { color: '#00e5ff', metalness: 0.9,  roughness: 0.1  }, // Cyan trim
  joint:   { color: '#020408', metalness: 1.0,  roughness: 0.05 }, // Near-black joints
  eye:     { color: '#00e5ff', emissive: '#00e5ff', emissiveIntensity: 25, metalness: 0, roughness: 0 }, // Bright cyan eyes
  glow:    { color: '#00e5ff', emissive: '#00e5ff', emissiveIntensity: 12, metalness: 0, roughness: 1 },
}

/* ──────────────────────────────────────────────
   HEAD — Rounded 'clean' aesthetic
 ────────────────────────────────────────────── */
function Head({ cur, gesture }: { cur: React.MutableRefObject<{x:number;y:number}>, gesture: string | null }) {
  const g = useRef<THREE.Group>(null)
  const eyeLight = useRef<THREE.PointLight>(null)
  const sy = useRef<Spring>({ value: 0, vel: 0 })
  const sx = useRef<Spring>({ value: 0, vel: 0 })
  const tilt = useRef<Spring>({ value: 0, vel: 0 })

  const smoothX = useRef(0)
  const smoothY = useRef(0)

  useFrame(({ clock }, dt) => {
    if (!g.current) return
    const c = cur.current
    const t = clock.elapsedTime

    smoothX.current = lerp(smoothX.current, c.x, 0.08)
    smoothY.current = lerp(smoothY.current, c.y, 0.08)

    const isIdle = Math.abs(c.x) < 0.05 && Math.abs(c.y) < 0.05
    const idleYaw = isIdle ? Math.sin(t * 0.3) * 0.05 : 0
    const idlePitch = isIdle ? Math.cos(t * 0.2) * 0.03 : 0

    const breathing = Math.sin(t * 1.2) * 0.005
    
    let targetYaw = smoothX.current * 0.4 + idleYaw
    let targetPitch = smoothY.current * 0.15 + breathing + idlePitch
    let targetTilt = smoothX.current * 0.08

    if (gesture) {
      if (gesture === 'left') { targetYaw = -0.5; targetPitch = 0.2 }
      if (gesture === 'right') { targetYaw = 0.5; targetPitch = 0.2 }
      if (gesture === 'center') { targetYaw = 0; targetPitch = 0.6 }
    }

    springStep(sy.current, targetYaw, 8, 6, dt)
    springStep(sx.current, targetPitch, 8, 6, dt)
    springStep(tilt.current, targetTilt, 7, 5, dt)

    g.current.rotation.y = sy.current.value
    g.current.rotation.x = sx.current.value
    g.current.rotation.z = tilt.current.value

    if (eyeLight.current) {
      eyeLight.current.intensity = 2 + Math.sin(t * 4) * 0.5
    }
  })

  return (
    <group ref={g} position={[0, 1.85, 0]}>
      {/* Main Helmet - Rounded */}
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[0.42, 64, 64]} />
        <meshStandardMaterial {...M.hull} />
      </mesh>
      
      {/* Visor Area - Dark inset */}
      <mesh position={[0, 0, 0.05]}>
        <sphereGeometry args={[0.4, 64, 64, 0, Math.PI * 2, 0.5, 2.2]} />
        <meshStandardMaterial color="#000000" roughness={0.05} metalness={1} />
      </mesh>

      {/* Eyes - Cyan glowing strips */}
      {[-0.14, 0.14].map((x, i) => (
        <group key={i} position={[x, 0.06, 0.38]}>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <capsuleGeometry args={[0.03, 0.08, 16, 16]} />
            <meshStandardMaterial {...M.eye} />
          </mesh>
        </group>
      ))}

      <pointLight ref={eyeLight} color="#00e5ff" intensity={2} distance={1.5} position={[0, 0.06, 0.45]} />
      
      {/* Ear Disks */}
      {[-0.41, 0.41].map((x, i) => (
        <mesh key={i} position={[x, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
          <cylinderGeometry args={[0.13, 0.13, 0.08, 64]} />
          <meshStandardMaterial {...M.panel} />
        </mesh>
      ))}
    </group>
  )
}

/* ──────────────────────────────────────────────
   NECK
 ────────────────────────────────────────────── */
function Neck() {
  return (
    <group position={[0, 1.48, 0]}>
      <mesh>
        <cylinderGeometry args={[0.08, 0.1, 0.25, 64]} />
        <meshStandardMaterial {...M.joint} />
      </mesh>
    </group>
  )
}

/* ──────────────────────────────────────────────
   TORSO — Rounded smooth chest
 ────────────────────────────────────────────── */
function Torso({ cur }: { cur: React.MutableRefObject<{x:number;y:number}> }) {
  const g = useRef<THREE.Group>(null)
  const sy = useRef<Spring>({ value: 0, vel: 0 })

  useFrame(({ clock }, dt) => {
    if (!g.current) return
    springStep(sy.current, cur.current.x * 0.08, 6, 5, dt)
    g.current.rotation.y = sy.current.value
  })

  return (
    <group ref={g}>
      {/* Main Chest - Rounded */}
      <mesh position={[0, 0.95, 0]} castShadow receiveShadow>
        <sphereGeometry args={[0.55, 64, 64]} />
        <meshStandardMaterial {...M.hull} />
      </mesh>
      
      {/* Shoulder Joints */}
      {[-0.6, 0.6].map((x, i) => (
        <mesh key={i} position={[x, 1.15, 0]} castShadow>
          <sphereGeometry args={[0.14, 32, 32]} />
          <meshStandardMaterial {...M.joint} />
        </mesh>
      ))}

      {/* Waist Segment */}
      <mesh position={[0, 0.6, 0]} castShadow>
        <cylinderGeometry args={[0.3, 0.38, 0.35, 64]} />
        <meshStandardMaterial {...M.panel} />
      </mesh>

      {/* Pelvis Area */}
      <mesh position={[0, 0.35, 0]} castShadow>
        <sphereGeometry args={[0.45, 64, 64]} />
        <meshStandardMaterial {...M.hull} />
      </mesh>
    </group>
  )
}

/* ──────────────────────────────────────────────
   ARM — side: -1 = left, +1 = right
 ────────────────────────────────────────────── */
function Arm({ side, cur, gesture }: { side: -1 | 1; cur: React.MutableRefObject<{x:number;y:number}>; gesture: string | null }) {
  const shoulderG = useRef<THREE.Group>(null)
  const elbowG    = useRef<THREE.Group>(null)
  const wristG    = useRef<THREE.Group>(null)

  const shX = useRef<Spring>({ value: -0.1, vel: 0 })
  const shZ = useRef<Spring>({ value: side * -0.15, vel: 0 })
  const elX = useRef<Spring>({ value: 0.4, vel: 0 })
  const wrZ = useRef<Spring>({ value: 0, vel: 0 })

  const smoothX = useRef(0)
  const smoothY = useRef(0)

  useFrame(({ clock }, dt) => {
    const c = cur.current
    const t = clock.elapsedTime

    smoothX.current = lerp(smoothX.current, c.x, 0.08)
    smoothY.current = lerp(smoothY.current, c.y, 0.08)

    let targetShX = -0.2 + smoothY.current * 0.3
    let targetShZ = side * (-0.45 + smoothX.current * -0.4 * side) 
    let elbowBend = 0.5 + Math.sqrt(smoothX.current**2 + smoothY.current**2) * 0.4
    let targetWrZ = smoothX.current * -0.3 * side

    // Gesture logic
    if (gesture) {
      // If we hover something, point at it
      const isRight = side === 1
      if ((gesture === 'right' && isRight) || (gesture === 'left' && !isRight)) {
        targetShX = -1.2 // Point forward/up
        targetShZ = side * -1.5 // Point outwards
        elbowBend = 0.1 // Straight arm
      } else if (gesture === 'center') {
        targetShX = 0.2 // Point down
        targetShZ = side * -0.4 // Closer to body
        elbowBend = 1.0 // Bend elbow
      }
    }

    springStep(shX.current, targetShX, 9, 6, dt)
    springStep(shZ.current, targetShZ, 9, 6, dt)
    springStep(elX.current, elbowBend, 9, 6, dt)
    springStep(wrZ.current, targetWrZ, 10, 6, dt)

    if (shoulderG.current) {
      shoulderG.current.rotation.x = shX.current.value
      shoulderG.current.rotation.z = shZ.current.value
    }
    if (elbowG.current) {
      elbowG.current.rotation.x = elX.current.value
    }
    if (wristG.current) {
      wristG.current.rotation.z = wrZ.current.value
    }
  })

  const s = side

  return (
    <group position={[s * 0.65, 1.2, 0]}>
      <mesh>
        <sphereGeometry args={[0.15, 32, 32]} />
        <meshStandardMaterial {...M.joint} />
      </mesh>

      <group ref={shoulderG}>
        {/* Upper arm */}
        <mesh position={[s * 0.2, 0, 0]} rotation={[0, 0, s * (Math.PI / 2)]} castShadow>
          <cylinderGeometry args={[0.1, 0.09, 0.35, 32]} />
          <meshStandardMaterial {...M.hull} />
        </mesh>

        <mesh position={[s * 0.4, 0, 0]}>
          <sphereGeometry args={[0.12, 32, 32]} />
          <meshStandardMaterial {...M.joint} />
        </mesh>

        <group ref={elbowG} position={[s * 0.4, 0, 0]}>
          {/* Forearm */}
          <mesh position={[s * 0.18, 0, 0]} rotation={[0, 0, s * (Math.PI / 2)]} castShadow>
            <cylinderGeometry args={[0.09, 0.08, 0.32, 32]} />
            <meshStandardMaterial {...M.panel} />
          </mesh>

          <mesh position={[s * 0.36, 0, 0]}>
            <sphereGeometry args={[0.09, 32, 32]} />
            <meshStandardMaterial {...M.joint} />
          </mesh>

          <group ref={wristG} position={[s * 0.36, 0, 0]}>
            {/* Rounded Palm */}
            <mesh position={[s * 0.08, 0, 0]} castShadow>
              <sphereGeometry args={[0.09, 32, 32]} />
              <meshStandardMaterial {...M.panel} />
            </mesh>

            {/* Fingertip glow */}
            <mesh position={[s * 0.16, 0.02, 0]}>
              <sphereGeometry args={[0.02, 16, 16]} />
              <meshStandardMaterial {...M.glow} />
            </mesh>
            <pointLight color="#00e5ff" intensity={1} distance={1} position={[s * 0.18, 0.02, 0]} />
          </group>
        </group>
      </group>
    </group>
  )
}

/* ──────────────────────────────────────────────
   BASE RING
────────────────────────────────────────────── */
function BaseRing() {
  const r1 = useRef<THREE.Mesh>(null)
  const r2 = useRef<THREE.Mesh>(null)
  useFrame(({ clock }) => {
    if (r1.current) r1.current.rotation.z =  clock.elapsedTime * 0.1
    if (r2.current) r2.current.rotation.z = -clock.elapsedTime * 0.05
  })
  return (
    <group position={[0, -0.6, 0]} rotation={[-Math.PI/2, 0, 0]}>
      <mesh ref={r1}>
        <ringGeometry args={[1.2, 1.4, 128]} />
        <meshStandardMaterial color="#00e5ff" emissive="#00e5ff" emissiveIntensity={0.5} transparent opacity={0.2} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={r2}>
        <ringGeometry args={[1.6, 1.62, 128]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.2} transparent opacity={0.1} side={THREE.DoubleSide} />
      </mesh>
      <ContactShadows resolution={1024} scale={10} blur={2} opacity={0.75} far={2} color="#000000" />
    </group>
  )
}

/* ──────────────────────────────────────────────
   CAMERA DRIFT
────────────────────────────────────────────── */
function CameraDrift({ cur }: { cur: React.MutableRefObject<{x:number;y:number}> }) {
  const cx = useRef<Spring>({ value: 0, vel: 0 })
  const cy = useRef<Spring>({ value: 0.9, vel: 0 })

  useFrame((state, dt) => {
    springStep(cx.current, cur.current.x * 0.2, 3, 3, dt)
    springStep(cy.current, 0.9 + cur.current.y * -0.1, 3, 3, dt)
    state.camera.position.x = cx.current.value
    state.camera.position.y = cy.current.value
    state.camera.lookAt(0, 1.1, 0)
  })
  return null
}

/* ──────────────────────────────────────────────
   EXPORTED CANVAS
────────────────────────────────────────────── */
export default function RobotScene({ cursorRef, gesture }: { cursorRef: React.MutableRefObject<{x:number;y:number}>; gesture: string | null }) {
  return (
    <Canvas
      camera={{ position: [0, 0.9, 5], fov: 38 }}
      shadows
      gl={{
        antialias: true,
        alpha: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.2,
      }}
      style={{ width: '100%', height: '100%' }}
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.8} color="#0a1a2a" />
        <pointLight position={[0, 3, 5]} intensity={3} color="#00e5ff" />
        <spotLight position={[0, 8, 6]} angle={0.3} penumbra={1} intensity={4} color="#00c8e0" castShadow />
        <directionalLight position={[-4, 4, 3]} intensity={2} color="#00e5ff" />
        <directionalLight position={[4, 4, 3]} intensity={2} color="#0088aa" />
        <pointLight position={[0, -2, 4]} intensity={1.5} color="#00e5ff" />
        
        <CameraDrift cur={cursorRef} />
        <BaseRing />
        
        <Float speed={2} rotationIntensity={0.1} floatIntensity={0.2}>
          <group position={[0, -0.8, 0]}>
            <Torso cur={cursorRef} />
            <Neck />
            <Head cur={cursorRef} gesture={gesture} />
            <Arm side={-1} cur={cursorRef} gesture={gesture} />
            <Arm side={1}  cur={cursorRef} gesture={gesture} />
          </group>
        </Float>
      </Suspense>
    </Canvas>
  )
}
