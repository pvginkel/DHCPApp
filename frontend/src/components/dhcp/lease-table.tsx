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
import { useSSEContext } from '@/contexts/sse-context'
import { useRef, useState, useEffect } from 'react'
import type { components } from '@/lib/api/generated/types'
import { useLeaseSorting } from '@/hooks/use-lease-sorting'
import { useLeaseFiltering } from '@/hooks/use-lease-filtering'
import { TableControls } from '@/components/dhcp/table-controls'
import { Button } from '@/components/ui/button'
import type { SortableField } from '@/types/lease'

type DhcpLease = components['schemas']['DhcpLease']

interface LeaseChangeState {
  [key: string]: {
    type: 'added' | 'updated' | 'removing';
    timestamp: number;
  };
}


export function LeaseTable() {
  const rawDataRef = useRef<DhcpLease[] | null>(null)
  const [displayState, setDisplayState] = useState<{
    leases: DhcpLease[];
    changes: LeaseChangeState;
  }>({ leases: [], changes: {} })
  const animationTimeoutRef = useRef<number | null>(null)
  const isAnimatingRef = useRef<boolean>(false)
  
  const { connectionStatus } = useSSEContext()

  const { data: rawLeases, isLoading, error } = useLeasesQuery()
  
  useEffect(() => {
    // If no new data, skip
    if (!rawLeases) {
      return
    }
    
    // Initial load - just set the display state without animation
    if (!rawDataRef.current) {
      rawDataRef.current = [...rawLeases]
      setDisplayState({ leases: rawLeases, changes: {} })
      return
    }
    
    // Compare with previous data to detect changes
    const newChanges: LeaseChangeState = {}
    const previousLeases = rawDataRef.current
    const currentTime = Date.now()
    
    const previousLeaseMap = new Map(
      previousLeases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
    )
    const currentLeaseMap = new Map(
      rawLeases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
    )
    
    // Check for added and updated leases
    for (const lease of rawLeases) {
      const leaseKey = `${lease.ip_address}-${lease.mac_address}`
      const previousLease = previousLeaseMap.get(leaseKey)
      
      if (!previousLease) {
        newChanges[leaseKey] = { type: 'added', timestamp: currentTime }
      } else if (JSON.stringify(previousLease) !== JSON.stringify(lease)) {
        newChanges[leaseKey] = { type: 'updated', timestamp: currentTime }
      }
    }
    
    // Check for removed leases
    for (const [leaseKey] of previousLeaseMap) {
      if (!currentLeaseMap.has(leaseKey)) {
        newChanges[leaseKey] = { type: 'removing', timestamp: currentTime }
      }
    }
    
    if (Object.keys(newChanges).length > 0) {
      // Create display state with all leases (including removed ones in original positions)
      const frozenDisplayLeases: DhcpLease[] = []
      const processedKeys = new Set<string>()
      
      // First, add all previous leases in their original order
      for (const prevLease of previousLeases) {
        const leaseKey = `${prevLease.ip_address}-${prevLease.mac_address}`
        const currentLease = currentLeaseMap.get(leaseKey)
        
        if (currentLease) {
          // Use updated data if available
          frozenDisplayLeases.push(currentLease)
        } else {
          // Keep removed lease in original position
          frozenDisplayLeases.push(prevLease)
        }
        processedKeys.add(leaseKey)
      }
      
      // Then add any new leases at the end
      for (const newLease of rawLeases) {
        const leaseKey = `${newLease.ip_address}-${newLease.mac_address}`
        if (!processedKeys.has(leaseKey)) {
          frozenDisplayLeases.push(newLease)
        }
      }
      
      // Phase 1: Show animations with frozen display state
      isAnimatingRef.current = true
      setDisplayState({
        leases: frozenDisplayLeases,
        changes: newChanges,
      })
      
      // Clear any existing timeout
      if (animationTimeoutRef.current) {
        clearTimeout(animationTimeoutRef.current)
      }
      
      // Phase 2: After animation completes, apply real data update
      animationTimeoutRef.current = window.setTimeout(() => {
        isAnimatingRef.current = false
        rawDataRef.current = [...rawLeases]
        setDisplayState({ leases: rawLeases, changes: {} })
      }, 1000)
    } else {
      // No changes detected, just update the display state
      rawDataRef.current = [...rawLeases]
      setDisplayState({ leases: rawLeases, changes: {} })
    }
  }, [rawLeases])

  // Cleanup timeout on unmount
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

  // Apply sorting and filtering to display leases
  const { sortConfig, sortedLeases, handleSort } = useLeaseSorting(displayState.leases)
  const { searchTerm, setSearchTerm, filteredLeases } = useLeaseFiltering(sortedLeases)
  
  // Final display leases after sorting and filtering
  const displayLeases = filteredLeases

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

  if (!displayLeases || displayLeases.length === 0) {
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

  const getSortIcon = (field: SortableField) => {
    if (sortConfig.field !== field) {
      return (
        <svg className="h-4 w-4 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      )
    }
    
    if (sortConfig.direction === 'asc') {
      return (
        <svg className="h-4 w-4 text-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      )
    } else if (sortConfig.direction === 'desc') {
      return (
        <svg className="h-4 w-4 text-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      )
    }
    
    return null
  }

  return (
    <div className="space-y-4">
      {connectionStatus.state === 'error' && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <div className="flex items-center space-x-2">
            <div className="h-4 w-4 rounded-full bg-yellow-500"></div>
            <div>
              <h4 className="text-sm font-medium text-yellow-800">Real-time updates unavailable</h4>
              <p className="text-sm text-yellow-600 mt-1">
                {connectionStatus.error || 'Connection to live updates failed. Data shown may not be current.'}
              </p>
            </div>
          </div>
        </div>
      )}
      
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
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('ip_address')}
                aria-label="Sort by IP Address"
              >
                <span className="flex items-center gap-1">
                  IP Address
                  {getSortIcon('ip_address')}
                </span>
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('mac_address')}
                aria-label="Sort by MAC Address"
              >
                <span className="flex items-center gap-1">
                  MAC Address
                  {getSortIcon('mac_address')}
                </span>
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('hostname')}
                aria-label="Sort by Hostname"
              >
                <span className="flex items-center gap-1">
                  Hostname
                  {getSortIcon('hostname')}
                </span>
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('vendor')}
                aria-label="Sort by Vendor"
              >
                <span className="flex items-center gap-1">
                  Vendor
                  {getSortIcon('vendor')}
                </span>
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('lease_time')}
                aria-label="Sort by Lease Expiration"
              >
                <span className="flex items-center gap-1">
                  Lease Expiration
                  {getSortIcon('lease_time')}
                </span>
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 font-semibold hover:bg-transparent"
                onClick={() => handleSort('is_active')}
                aria-label="Sort by Status"
              >
                <span className="flex items-center gap-1">
                  Status
                  {getSortIcon('is_active')}
                </span>
              </Button>
            </TableHead>
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
              >
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
                  {lease.vendor || <span className="text-muted-foreground italic">Unknown</span>}
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
    </div>
  )
}