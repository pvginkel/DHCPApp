import { createFileRoute } from '@tanstack/react-router'
import { LeaseTable } from '@/components/dhcp/lease-table'
import { StatsCards } from '@/components/dhcp/stats-cards'
import { useSSEConnection } from '@/hooks/use-sse-connection'
import { formatConnectionStatus } from '@/lib/utils/sse-utils'

function HomePage() {
  const { connectionStatus } = useSSEConnection();
  const { label, color } = formatConnectionStatus(connectionStatus.state);
  
  const dotColor = connectionStatus.state === 'connected' 
    ? 'bg-green-500' 
    : connectionStatus.state === 'connecting'
    ? 'bg-yellow-500'
    : 'bg-red-500';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">DHCP Leases</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of active DHCP lease assignments
          </p>
        </div>
        <div className="flex items-center space-x-2" title={connectionStatus.error || `Connection: ${connectionStatus.state}`}>
          <div className={`h-2 w-2 rounded-full ${dotColor}`}></div>
          <span className={`text-sm ${color}`}>{label}</span>
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
