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
import { useSSEConnection } from '@/hooks/use-sse-connection'
import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useRef, useState, useEffect } from 'react'
import { isDataChangedEvent } from '@/lib/utils/sse-utils'
import type { SSEEvent } from '@/types/sse'
import { apiKeys } from '@/lib/api/generated/queries'
import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

interface LeaseChangeState {
  [key: string]: {
    type: 'added' | 'updated' | 'removing';
    timestamp: number;
  };
}

interface AnimationPhase {
  displayLeases: DhcpLease[];
  changes: LeaseChangeState;
}

export function LeaseTable() {
  const queryClient = useQueryClient()
  const previousLeasesRef = useRef<DhcpLease[]>([])
  const [animationPhase, setAnimationPhase] = useState<AnimationPhase | null>(null)
  const [pendingUpdates, setPendingUpdates] = useState<boolean>(false)
  const animationTimeoutRef = useRef<number | null>(null)
  const updateQueueRef = useRef<(() => void)[]>([])
  
  const handleSSEEvent = useCallback((event: SSEEvent) => {
    if (isDataChangedEvent(event)) {
      const updateFunction = () => {
        queryClient.invalidateQueries({ queryKey: [...apiKeys.all, 'leases'] })
        queryClient.invalidateQueries({ queryKey: [...apiKeys.all, 'status'] })
      }
      
      // If animation is in progress, queue the update
      if (animationPhase) {
        updateQueueRef.current.push(updateFunction)
        setPendingUpdates(true)
      } else {
        updateFunction()
      }
    }
  }, [queryClient, animationPhase])

  const handleSSEError = useCallback((error: Error) => {
    console.warn('SSE connection error:', error.message)
  }, [])

  const { connectionStatus } = useSSEConnection({
    onEvent: handleSSEEvent,
    onError: handleSSEError,
    autoConnect: true,
    maxReconnectAttempts: 10,
  })

  const { data: leases, isLoading, error } = useLeasesQuery()
  
  useEffect(() => {
    // Skip processing if we're currently animating
    if (animationPhase) {
      return
    }
    
    // Only trigger animations if we have previous leases to compare against
    // This prevents animations on initial load
    if (leases && previousLeasesRef.current.length > 0) {
      const newChanges: LeaseChangeState = {}
      const previousLeases = previousLeasesRef.current
      const currentTime = Date.now()
      
      const previousLeaseMap = new Map(
        previousLeases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
      )
      const currentLeaseMap = new Map(
        leases.map(lease => [`${lease.ip_address}-${lease.mac_address}`, lease])
      )
      
      // Check for added and updated leases
      for (const lease of leases) {
        const leaseKey = `${lease.ip_address}-${lease.mac_address}`
        const previousLease = previousLeaseMap.get(leaseKey)
        
        if (!previousLease) {
          newChanges[leaseKey] = { type: 'added', timestamp: currentTime }
        } else if (JSON.stringify(previousLease) !== JSON.stringify(lease)) {
          newChanges[leaseKey] = { type: 'updated', timestamp: currentTime }
        }
      }
      
      // Check for removed leases
      const removedLeases: DhcpLease[] = []
      for (const [leaseKey, lease] of previousLeaseMap) {
        if (!currentLeaseMap.has(leaseKey)) {
          newChanges[leaseKey] = { type: 'removing', timestamp: currentTime }
          removedLeases.push(lease)
        }
      }
      
      if (Object.keys(newChanges).length > 0) {
        // Phase 1: Create frozen state with all leases (including removed ones in original positions)
        // Merge previous leases with new ones, keeping original order for removed items
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
        for (const newLease of leases) {
          const leaseKey = `${newLease.ip_address}-${newLease.mac_address}`
          if (!processedKeys.has(leaseKey)) {
            frozenDisplayLeases.push(newLease)
          }
        }
        
        // Start Phase 1: Show animations in original positions
        setAnimationPhase({
          displayLeases: frozenDisplayLeases,
          changes: newChanges,
        })
        
        // Clear any existing timeout
        if (animationTimeoutRef.current) {
          clearTimeout(animationTimeoutRef.current)
        }
        
        // Phase 2: After animation completes, apply real data update
        animationTimeoutRef.current = window.setTimeout(() => {
          setAnimationPhase(null)
          previousLeasesRef.current = [...leases]
          
          // Process any queued updates
          if (updateQueueRef.current.length > 0) {
            const queuedUpdates = [...updateQueueRef.current]
            updateQueueRef.current = []
            setPendingUpdates(false)
            
            // Execute queued updates
            queuedUpdates.forEach(update => update())
          }
        }, 1000)
      }
    }
    
    if (leases && !animationPhase) {
      previousLeasesRef.current = [...leases]
    }
  }, [leases, animationPhase])

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
    const change = animationPhase?.changes[leaseKey]
    
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

  // Use animation phase display leases if animating, otherwise use current leases
  const displayLeases = animationPhase ? animationPhase.displayLeases : (leases || [])

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
      
      {pendingUpdates && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
          <div className="flex items-center space-x-2">
            <div className="h-3 w-3 rounded-full bg-blue-500 animate-pulse"></div>
            <p className="text-sm text-blue-600">
              Updates pending... (processing after animation completes)
            </p>
          </div>
        </div>
      )}
      
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