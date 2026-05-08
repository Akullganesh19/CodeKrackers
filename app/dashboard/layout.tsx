import Sidebar from '@/app/components/Sidebar'
import Breadcrumbs from '@/app/components/Breadcrumbs'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-obsidian overflow-hidden">
      {/* Persistent Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-y-auto scrollbar-hide">
        <div className="absolute inset-0 bg-grid-white/[0.02] -z-10" />
        <div className="min-h-full p-4 md:p-8 lg:p-12">
          <Breadcrumbs />
          {children}
        </div>
      </main>
    </div>
  )
}