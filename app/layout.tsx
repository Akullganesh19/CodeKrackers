import type { Metadata } from "next"
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import RobotBackground from "@/components/RobotBackground"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" })
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" })

export const metadata: Metadata = {
  title: "VSDP | Vishing & Smishing Defense Platform",
  description: "AI-powered detection, honeypot baiting, and blockchain evidence for India's digital future.",
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} antialiased bg-bg`}>
        {/* Persistent robot — visible on every page */}
        <RobotBackground />

        {/* Global aesthetic overlays */}
        <div className="scanlines" />
        <div className="grid-overlay" />
        <div className="vignette" />

        {/* Page content — sits above robot */}
        <div style={{ position: 'relative', zIndex: 10, backgroundColor: 'transparent' }}>
          {children}
        </div>
      </body>
    </html>
  )
}
