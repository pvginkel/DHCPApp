# API Usage Examples

This document shows how to use the generated API types and hooks in your React components.

## Basic Usage

### Fetching DHCP Leases

```typescript
import { useDhcpLeasesTransformed } from '@/api/utils'
import type { DHCPLease } from '@/types/app'

function DHCPLeasesList() {
  const { 
    data: leases, 
    isLoading, 
    error 
  } = useDhcpLeasesTransformed({
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  if (isLoading) return <div>Loading leases...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!leases) return <div>No leases found</div>

  return (
    <div>
      <h2>DHCP Leases ({leases.length})</h2>
      {leases.map((lease: DHCPLease) => (
        <div key={lease.id} className="border p-4 mb-2">
          <div className="font-bold">{lease.ipAddress}</div>
          <div>MAC: {lease.macAddress}</div>
          <div>Hostname: {lease.hostname || 'Unknown'}</div>
          <div>Status: {lease.status}</div>
          <div>Device Type: {lease.deviceType || 'Unknown'}</div>
          <div>Static: {lease.isStatic ? 'Yes' : 'No'}</div>
        </div>
      ))}
    </div>
  )
}
```

### Health Check

```typescript
import { useHealthCheck } from '@/api/utils'

function HealthStatus() {
  const { data: health, isLoading } = useHealthCheck()

  if (isLoading) return <div>Checking health...</div>

  return (
    <div className={`p-2 rounded ${health?.status === 'healthy' ? 'bg-green-100' : 'bg-red-100'}`}>
      Service: {health?.service} - Status: {health?.status}
    </div>
  )
}
```

## Advanced Usage

### Custom Data Transformation

```typescript
import { useDhcpLeases } from '@/api/utils'
import { convertApiLeasesToFrontend, inferDeviceType } from '@/api/utils'

function CustomLeasesList() {
  const { data: apiLeases, isLoading } = useDhcpLeases()

  // Custom transformation
  const transformedLeases = useMemo(() => {
    if (!apiLeases) return []
    
    return convertApiLeasesToFrontend(apiLeases)
      .filter(lease => lease.isActive) // Only active leases
      .sort((a, b) => a.ipAddress.localeCompare(b.ipAddress)) // Sort by IP
      .map(lease => ({
        ...lease,
        deviceType: inferDeviceType(lease.hostname) || 'Unknown',
        isNew: false, // Could be determined by comparing with previous data
      }))
  }, [apiLeases])

  return (
    <div>
      {/* Render transformedLeases */}
    </div>
  )
}
```

### Direct API Client Usage

```typescript
import { apiClient } from '@/api/client'
import { convertApiLeaseToFrontend } from '@/api/utils'

async function fetchSpecificLease(ipAddress: string) {
  try {
    const { data: leases, error } = await apiClient.GET('/leases')
    
    if (error) {
      console.error('API Error:', error)
      return null
    }

    // Find specific lease by IP
    const lease = leases?.find(l => l.ip_address === ipAddress)
    
    if (!lease) {
      console.log('Lease not found for IP:', ipAddress)
      return null
    }

    // Transform to frontend format
    return convertApiLeaseToFrontend(lease)
    
  } catch (error) {
    console.error('Network error:', error)
    return null
  }
}
```

### Error Handling

```typescript
import { useDhcpLeasesTransformed } from '@/api/utils'
import type { components } from '@/api/types'

type ApiError = components['schemas']['Error']

function DHCPLeasesWithErrorHandling() {
  const { data: leases, error, isError } = useDhcpLeasesTransformed()

  if (isError && error) {
    // Type-safe error handling
    const apiError = error as any
    
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <h3>Error loading DHCP leases</h3>
        <p><strong>Error:</strong> {apiError.error || 'Unknown error'}</p>
        {apiError.details && (
          <p><strong>Details:</strong> {apiError.details}</p>
        )}
      </div>
    )
  }

  return (
    <div>
      {/* Normal lease rendering */}
    </div>
  )
}
```

## Type Usage

### Working with Generated Types

```typescript
import type { 
  DhcpLeaseAPI, 
  DHCPLease, 
  components 
} from '@/api/types'

// API response type
type LeasesResponse = components['schemas']['DhcpLease'][]

// Error response type  
type ErrorResponse = components['schemas']['Error']

// API paths type (for advanced usage)
type ApiPaths = paths['/leases']['get']['responses']['200']['content']['application/json']

// Custom type guards
function isApiError(error: unknown): error is ErrorResponse {
  return typeof error === 'object' && 
         error !== null && 
         'error' in error
}

function isDhcpLease(data: unknown): data is DhcpLeaseAPI {
  return typeof data === 'object' && 
         data !== null && 
         'ip_address' in data && 
         'mac_address' in data
}
```

## Query Invalidation and Refetching

```typescript
import { useQueryClient } from '@tanstack/react-query'
import { apiKeys } from '@/api/utils'

function RefreshButton() {
  const queryClient = useQueryClient()

  const handleRefresh = () => {
    // Invalidate and refetch leases
    queryClient.invalidateQueries({ queryKey: apiKeys.list('leases') })
  }

  const handleRefreshAll = () => {
    // Invalidate all API queries
    queryClient.invalidateQueries({ queryKey: apiKeys.all })
  }

  return (
    <div>
      <button onClick={handleRefresh} className="mr-2">
        Refresh Leases
      </button>
      <button onClick={handleRefreshAll}>
        Refresh All
      </button>
    </div>
  )
}
```
