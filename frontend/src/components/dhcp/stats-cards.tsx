// Stats cards component with real-time data
import { useLeasesQuery } from '@/lib/api/generated/queries'
import { usePoolsQuery } from '@/lib/api/pools'
import {
  calculateTotalLeases,
  calculateAvailableIPs,
  calculateExpiringToday,
  calculateDeviceTypes,
} from '@/lib/utils/stats-utils'

interface StatCardProps {
  title: string
  value: string | number
  description: string
  isLoading?: boolean
  hasError?: boolean
}

function StatCard({ title, value, description, isLoading, hasError }: StatCardProps) {
  const displayValue = isLoading ? '...' : hasError ? '--' : value.toString()
  
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="text-sm font-medium">{title}</h3>
      </div>
      <div className="text-2xl font-bold">{displayValue}</div>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  )
}

export function StatsCards() {
  const { data: leases, isLoading: leasesLoading, error: leasesError } = useLeasesQuery()
  const { data: pools, isLoading: poolsLoading, error: poolsError } = usePoolsQuery()
  
  const isLoading = leasesLoading || poolsLoading
  const hasError = !!(leasesError || poolsError)
  
  // Calculate stats when data is available
  const stats = {
    totalLeases: leases ? calculateTotalLeases(leases) : 0,
    availableIPs: (leases && pools) ? calculateAvailableIPs(pools, leases) : 0,
    expiringToday: leases ? calculateExpiringToday(leases) : 0,
    deviceTypes: leases ? calculateDeviceTypes(leases) : 0,
  }
  
  return (
    <div className="grid gap-4 md:grid-cols-4">
      <StatCard
        title="Total Leases"
        value={stats.totalLeases}
        description="Active DHCP assignments"
        isLoading={isLoading}
        hasError={hasError}
      />
      <StatCard
        title="Available IPs"
        value={stats.availableIPs}
        description="Remaining in pool"
        isLoading={isLoading}
        hasError={hasError || (!pools && !poolsLoading)}
      />
      <StatCard
        title="Expiring Today"
        value={stats.expiringToday}
        description="By end of day"
        isLoading={isLoading}
        hasError={hasError}
      />
      <StatCard
        title="Device Types"
        value={stats.deviceTypes}
        description="Unique manufacturers"
        isLoading={isLoading}
        hasError={hasError}
      />
    </div>
  )
}