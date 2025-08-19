import { createFileRoute } from '@tanstack/react-router'
import { LeaseTable } from '@/components/dhcp/lease-table'
import { StatsCards } from '@/components/dhcp/stats-cards'

function HomePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">DHCP Leases</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of active DHCP lease assignments
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 rounded-full bg-green-500"></div>
          <span className="text-sm text-muted-foreground">Live</span>
        </div>
      </div>
      
      <LeaseTable />
      
      <StatsCards />
    </div>
  )
}

export const Route = createFileRoute('/')({
  component: HomePage,
})
