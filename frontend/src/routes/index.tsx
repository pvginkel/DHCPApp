import { createFileRoute } from '@tanstack/react-router'
import { LeaseTable } from '@/components/dhcp/lease-table'
import { StatsCards } from '@/components/dhcp/stats-cards'
import { useDataChangeSse } from '@/hooks/use-data-change-sse'
import { useDhcpLeases } from '@/lib/api/generated/hooks'

function HomePage() {
  const { isConnected } = useDataChangeSse()
  const { data: leases, isLoading, error } = useDhcpLeases()

  const dotColor = isConnected ? 'bg-green-500' : 'bg-red-500'
  const statusLabel = isConnected ? 'Live' : 'Disconnected'
  const statusColor = isConnected ? 'text-green-600' : 'text-red-600'

  return (
    <div className="space-y-6 p-6" data-testid="home-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">DHCP Leases</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of active DHCP lease assignments
          </p>
        </div>
        <div className="flex items-center space-x-2" title={`Connection: ${isConnected ? 'connected' : 'disconnected'}`} data-testid="sse-status">
          <div className={`h-2 w-2 rounded-full ${dotColor}`} data-testid="sse-status-dot"></div>
          <span className={`text-sm ${statusColor}`} data-testid="sse-status-label">{statusLabel}</span>
        </div>
      </div>

      <LeaseTable leases={leases} isLoading={isLoading} error={error} />

      <StatsCards leases={leases} isLoading={isLoading} error={error} />
    </div>
  )
}

export const Route = createFileRoute('/')({
  component: HomePage,
})
