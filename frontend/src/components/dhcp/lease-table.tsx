import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { LoadingSpinner } from "@/components/common/loading-spinner"
import type { TableProps } from "@/types/app"
import type { DhcpLease } from "@/lib/api/utils"
import { getDhcpLeaseKey, getDhcpLeaseStatus } from "@/lib/api/utils"

interface LeaseTableProps extends Omit<TableProps<DhcpLease>, 'columns'> {
  data: DhcpLease[]
}

export function LeaseTable({ data, sortConfig, onSort, isLoading, emptyMessage = "No leases found" }: LeaseTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-muted-foreground">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onSort('ip_address')}
            >
              IP Address
              {sortConfig.key === 'ip_address' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onSort('mac_address')}
            >
              MAC Address
              {sortConfig.key === 'mac_address' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onSort('hostname')}
            >
              Hostname
              {sortConfig.key === 'hostname' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onSort('lease_time')}
            >
              Lease Expiration
              {sortConfig.key === 'lease_time' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((lease) => {
            const status = getDhcpLeaseStatus(lease)
            return (
              <TableRow 
                key={getDhcpLeaseKey(lease)}
                className="hover:bg-muted/50"
              >
                <TableCell className="font-mono">{lease.ip_address}</TableCell>
                <TableCell className="font-mono">{lease.mac_address}</TableCell>
                <TableCell>{lease.hostname || 'Unknown'}</TableCell>
                <TableCell>{new Date(lease.lease_time).toLocaleString()}</TableCell>
                <TableCell>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {status}
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
