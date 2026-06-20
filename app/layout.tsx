import type { Metadata } from "next"
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import SessionMonitor from "@/backend/core/SessionMonitor"
import { AuthProvider } from "@/backend/core/AuthProvider"
import ClientLayout from "./client-layout"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" })
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" })

export const metadata: Metadata = {
  title: "VSDP | Vishing & Smishing Defense Platform — National Cybersecurity Command",
  description:
    "AI-powered detection, honeypot baiting, blockchain evidence, and auto-FIR filing system. India's sovereign digital defense infrastructure against vishing and smishing threats.",
  keywords: [
    "vishing detection", "smishing scanner", "AI voice clone detection",
    "cybersecurity India", "fraud detection", "honeypot baiting",
    "CERT-In", "cybercrime.gov.in", "VSDP",
  ],
  openGraph: {
    title: "VSDP — National Cybersecurity Command",
    description: "India's sovereign defense against vishing & smishing threats.",
    type: "website",
  },
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} antialiased`}>
        {/* Global aesthetic overlays */}
        <div className="grid-bg" />
        <div className="scan-overlay" />
        <div className="vignette" />

        {/* Content */}
        <div style={{ position: "relative", zIndex: 10 }}>
          <ClientLayout>
            <AuthProvider>
            {children}
            <SessionMonitor soundUrl="/sounds/cyber-alert.mp3" />
          </AuthProvider>
          </ClientLayout>
        </div>
      </body>
    </html>
  )
}