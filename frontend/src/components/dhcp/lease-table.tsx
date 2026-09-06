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
import { useRef, useState, useEffect } from 'react'
import type { DhcpLease, SortableField } from '@/types/lease'
import { useLeaseSorting } from '@/hooks/use-lease-sorting'
import { useLeaseFiltering } from '@/hooks/use-lease-filtering'
import { TableControls } from '@/components/dhcp/table-controls'
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react'

interface LeaseChangeState {
  [key: string]: {
    type: 'added' | 'updated' | 'removing';
    timestamp: number;
  };
}

interface LeaseTableProps {
  leases: DhcpLease[] | undefined
  isLoading: boolean
  error: Error | null
}

export function LeaseTable({ leases: rawLeases, isLoading, error }: LeaseTableProps) {
  const rawDataRef = useRef<DhcpLease[] | null>(null)
  const [displayState, setDisplayState] = useState<{
    leases: DhcpLease[];
    changes: LeaseChangeState;
  }>({ leases: [], changes: {} })
  const animationTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    if (!rawLeases) {
      return
    }

    if (!rawDataRef.current) {
      rawDataRef.current = [...rawLeases]
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Intentional: syncing external query data to display state on initial load
      setDisplayState({ leases: rawLeases, changes: {} })
      return
    }

    const newChanges: LeaseChangeState = {}
    const previousLeases = rawDataRef.current
    // eslint-disable-next-line no-restricted-properties -- Using Date.now() for animation timestamps, not ID generation
    const currentTime = Date.now()

    const previousLeaseMap = new Map(
      previousLeases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
    )
    const currentLeaseMap = new Map(
      rawLeases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
    )

    for (const lease of rawLeases) {
      const leaseKey = `${lease.ip_address}-${lease.mac_address}`
      const previousLease = previousLeaseMap.get(leaseKey)

      if (!previousLease) {
        newChanges[leaseKey] = { type: 'added', timestamp: currentTime }
      } else if (JSON.stringify(previousLease) !== JSON.stringify(lease)) {
        newChanges[leaseKey] = { type: 'updated', timestamp: currentTime }
      }
    }

    for (const [leaseKey] of previousLeaseMap) {
      if (!currentLeaseMap.has(leaseKey)) {
        newChanges[leaseKey] = { type: 'removing', timestamp: currentTime }
      }
    }

    if (Object.keys(newChanges).length > 0) {
      const frozenDisplayLeases: DhcpLease[] = []
      const processedKeys = new Set<string>()

      for (const prevLease of previousLeases) {
        const leaseKey = `${prevLease.ip_address}-${prevLease.mac_address}`
        const currentLease = currentLeaseMap.get(leaseKey)

        if (currentLease) {
          frozenDisplayLeases.push(currentLease)
        } else {
          frozenDisplayLeases.push(prevLease)
        }
        processedKeys.add(leaseKey)
      }

      for (const newLease of rawLeases) {
        const leaseKey = `${newLease.ip_address}-${newLease.mac_address}`
        if (!processedKeys.has(leaseKey)) {
          frozenDisplayLeases.push(newLease)
        }
      }

      setDisplayState({
        leases: frozenDisplayLeases,
        changes: newChanges,
      })

      if (animationTimeoutRef.current) {
        clearTimeout(animationTimeoutRef.current)
      }

      animationTimeoutRef.current = window.setTimeout(() => {
        rawDataRef.current = [...rawLeases]
        setDisplayState({ leases: rawLeases, changes: {} })
      }, 1000)
    } else {
      rawDataRef.current = [...rawLeases]
      setDisplayState({ leases: rawLeases, changes: {} })
    }
  }, [rawLeases])

  useEffect(() => {
    return () => {
      if (animationTimeoutRef.current) {
        clearTimeout(animationTimeoutRef.current)
      }
    }
  }, [])

  const getRowClassName = (lease: DhcpLease) => {
    const leaseKey = `${lease.ip_address}-${lease.mac_address}`
    const change = displayState.changes[leaseKey]

    if (!change) return ''

    switch (change.type) {
      case 'added':
        return 'lease-flash-added'
      case 'updated':
        return 'lease-flash-updated'
      case 'removing':
        return 'lease-flash-removing'
      default:
        return ''
    }
  }

  const { sortConfig, sortedLeases, handleSort } = useLeaseSorting(displayState.leases)
  const { searchTerm, setSearchTerm, filteredLeases } = useLeaseFiltering(sortedLeases)
  const displayLeases = filteredLeases

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8" data-testid="lease-table-loading">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full border-2 border-current border-t-transparent h-8 w-8 mx-auto" role="status" aria-label="Loading">
            <span className="sr-only">Loading...</span>
          </div>
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
      <div className="rounded-lg border border-red-200 bg-red-50 p-8" data-testid="lease-table-error">
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

  if (!displayLeases || displayLeases.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-8" data-testid="lease-table-empty">
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

  const getSortIcon = (field: SortableField) => {
    if (sortConfig.field !== field) {
      return <ArrowUpDown className="h-4 w-4 text-muted-foreground/50" />
    }

    if (sortConfig.direction === 'asc') {
      return <ArrowUp className="h-4 w-4 text-foreground" />
    } else if (sortConfig.direction === 'desc') {
      return <ArrowDown className="h-4 w-4 text-foreground" />
    }

    return null
  }

  const sortableColumns: { field: SortableField; label: string }[] = [
    { field: 'ip_address', label: 'IP Address' },
    { field: 'mac_address', label: 'MAC Address' },
    { field: 'hostname', label: 'Hostname' },
    { field: 'vendor', label: 'Vendor' },
    { field: 'lease_time', label: 'Lease Expiration' },
    { field: 'is_active', label: 'Status' },
  ]

  return (
    <div className="space-y-4" data-testid="lease-table">
      <div className="rounded-lg border border-border">
        <TableControls
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          totalCount={displayState.leases.length}
          filteredCount={displayLeases.length}
        />
        <Table>
          <TableHeader>
            <TableRow>
              {sortableColumns.map(({ field, label }) => (
                <TableHead key={field}>
                  <button
                    className="inline-flex items-center gap-1 h-auto p-0 font-semibold bg-transparent border-none cursor-pointer hover:text-foreground text-muted-foreground"
                    onClick={() => handleSort(field)}
                    aria-label={`Sort by ${label}`}
                    data-testid={`sort-${field}`}
                  >
                    {label}
                    {getSortIcon(field)}
                  </button>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayLeases.map((lease) => {
              const status = getLeaseStatus(lease)
              const statusDisplay = getLeaseStatusDisplay(status)

              return (
                <TableRow
                  key={`${lease.ip_address}-${lease.mac_address}`}
                  className={getRowClassName(lease)}
                  data-testid="lease-row"
                >
                  <TableCell className="font-mono" data-testid="lease-ip">
                    {lease.ip_address}
                  </TableCell>
                  <TableCell className="font-mono" data-testid="lease-mac">
                    {formatMacAddress(lease.mac_address)}
                  </TableCell>
                  <TableCell data-testid="lease-hostname">
                    {lease.hostname || <span className="text-muted-foreground italic">Unknown</span>}
                  </TableCell>
                  <TableCell data-testid="lease-vendor">
                    {lease.vendor || <span className="text-muted-foreground italic">Unknown</span>}
                  </TableCell>
                  <TableCell data-testid="lease-expiration">
                    {formatLeaseExpiration(lease.lease_time)}
                  </TableCell>
                  <TableCell data-testid="lease-status">
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
    </div>
  )
}
