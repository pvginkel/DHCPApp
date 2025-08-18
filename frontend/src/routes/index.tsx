import { createFileRoute } from '@tanstack/react-router'
import { LeaseTable } from '@/components/dhcp/lease-table'

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
      
      {/* Placeholder stats cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Total Leases</h3>
          </div>
          <div className="text-2xl font-bold">--</div>
          <p className="text-xs text-muted-foreground">
            Active DHCP assignments
          </p>
        </div>
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Available IPs</h3>
          </div>
          <div className="text-2xl font-bold">--</div>
          <p className="text-xs text-muted-foreground">
            Remaining in pool
          </p>
        </div>
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Expiring Soon</h3>
          </div>
          <div className="text-2xl font-bold">--</div>
          <p className="text-xs text-muted-foreground">
            Within 24 hours
          </p>
        </div>
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">New Devices</h3>
          </div>
          <div className="text-2xl font-bold">--</div>
          <p className="text-xs text-muted-foreground">
            Last 24 hours
          </p>
        </div>
      </div>
    </div>
  )
}

export const Route = createFileRoute('/')({
  component: HomePage,
})
