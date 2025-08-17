import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { LoadingSpinner } from "@/components/common/loading-spinner"
import type { DHCPLease, TableProps } from "@/types/app"

interface LeaseTableProps extends Omit<TableProps<DHCPLease>, 'columns'> {
  data: DHCPLease[]
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
              onClick={() => onSort('ipAddress')}
            >
              IP Address
              {sortConfig.key === 'ipAddress' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onSort('macAddress')}
            >
              MAC Address
              {sortConfig.key === 'macAddress' && (
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
              onClick={() => onSort('leaseEnd')}
            >
              Lease Expiration
              {sortConfig.key === 'leaseEnd' && (
                <span className="ml-1">
                  {sortConfig.direction === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((lease) => (
            <TableRow 
              key={lease.id}
              className={lease.isNew ? "animate-flash-update" : ""}
            >
              <TableCell className="font-mono">{lease.ipAddress}</TableCell>
              <TableCell className="font-mono">{lease.macAddress}</TableCell>
              <TableCell>{lease.hostname || 'Unknown'}</TableCell>
              <TableCell>{new Date(lease.leaseEnd).toLocaleString()}</TableCell>
              <TableCell>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  lease.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {lease.status}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
