import { useLeasesQuery } from '@/lib/api/generated/queries'
import { LoadingSpinner } from '@/components/common/loading-spinner'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { 
  formatLeaseExpiration, 
  formatMacAddress, 
  getLeaseStatus, 
  getLeaseStatusDisplay 
} from '@/lib/utils/lease-utils'

export function LeaseTable() {
  const { data: leases, isLoading, error } = useLeasesQuery()

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
          <div>
            <h3 className="text-lg font-medium">Loading DHCP leases...</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Fetching current lease information from the DHCP server.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-8">
        <div className="text-center space-y-4">
          <div>
            <h3 className="text-lg font-medium text-red-800">Failed to load DHCP leases</h3>
            <p className="text-sm text-red-600 mt-2">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (!leases || leases.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-8">
        <div className="text-center space-y-4">
          <div>
            <h3 className="text-lg font-medium">No DHCP leases found</h3>
            <p className="text-sm text-muted-foreground mt-2">
              No active or expired DHCP leases are currently available.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>IP Address</TableHead>
            <TableHead>MAC Address</TableHead>
            <TableHead>Hostname</TableHead>
            <TableHead>Lease Expiration</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {leases.map((lease) => {
            const status = getLeaseStatus(lease)
            const statusDisplay = getLeaseStatusDisplay(status)
            
            return (
              <TableRow key={`${lease.ip_address}-${lease.mac_address}`}>
                <TableCell className="font-mono">
                  {lease.ip_address}
                </TableCell>
                <TableCell className="font-mono">
                  {formatMacAddress(lease.mac_address)}
                </TableCell>
                <TableCell>
                  {lease.hostname || <span className="text-muted-foreground italic">Unknown</span>}
                </TableCell>
                <TableCell>
                  {formatLeaseExpiration(lease.lease_time)}
                </TableCell>
                <TableCell>
                  <span className={statusDisplay.className}>
                    {statusDisplay.label}
                  </span>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}