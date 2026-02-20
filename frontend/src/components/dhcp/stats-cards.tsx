import { usePoolsQuery } from '@/lib/api/pools'
import {
  calculateTotalLeases,
  calculateAvailableIPs,
  calculateExpiringToday,
  calculateDeviceTypes,
} from '@/lib/utils/stats-utils'
import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

interface StatCardProps {
  title: string
  value: string | number
  description: string
  isLoading?: boolean
  hasError?: boolean
  testId?: string
}

function StatCard({ title, value, description, isLoading, hasError, testId }: StatCardProps) {
  const displayValue = isLoading ? '...' : hasError ? '--' : value.toString()

  return (
    <div className="rounded-lg border border-border bg-card p-6" data-testid={testId}>
      <div className="flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="text-sm font-medium">{title}</h3>
      </div>
      <div className="text-2xl font-bold" data-testid={testId ? `${testId}.value` : undefined}>{displayValue}</div>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  )
}

interface StatsCardsProps {
  leases: DhcpLease[] | undefined
  isLoading: boolean
  error: Error | null
}

export function StatsCards({ leases, isLoading: leasesLoading, error: leasesError }: StatsCardsProps) {
  const { data: pools, isLoading: poolsLoading, error: poolsError } = usePoolsQuery()

  const isLoading = leasesLoading || poolsLoading
  const hasError = !!(leasesError || poolsError)

  const stats = {
    totalLeases: leases ? calculateTotalLeases(leases) : 0,
    availableIPs: (leases && pools) ? calculateAvailableIPs(pools, leases) : 0,
    expiringToday: leases ? calculateExpiringToday(leases) : 0,
    deviceTypes: leases ? calculateDeviceTypes(leases) : 0,
  }

  return (
    <div className="grid gap-4 md:grid-cols-4" data-testid="stats-cards">
      <StatCard
        title="Total Leases"
        value={stats.totalLeases}
        description="Active DHCP assignments"
        isLoading={isLoading}
        hasError={hasError}
        testId="stat-total-leases"
      />
      <StatCard
        title="Available IPs"
        value={stats.availableIPs}
        description="Remaining in pool"
        isLoading={isLoading}
        hasError={hasError || (!pools && !poolsLoading)}
        testId="stat-available-ips"
      />
      <StatCard
        title="Expiring Today"
        value={stats.expiringToday}
        description="By end of day"
        isLoading={isLoading}
        hasError={hasError}
        testId="stat-expiring-today"
      />
      <StatCard
        title="Device Types"
        value={stats.deviceTypes}
        description="Unique manufacturers"
        isLoading={isLoading}
        hasError={hasError}
        testId="stat-device-types"
      />
    </div>
  )
}
