// API utilities - simplified for BFF pattern
import type { components } from './generated/types'

// Type aliases for cleaner imports
export type DhcpLease = components['schemas']['DhcpLease']

/**
 * Utility function to generate React keys for DHCP leases
 * @param lease - The lease object from the API
 * @returns Unique key for React rendering
 */
export function getDhcpLeaseKey(lease: DhcpLease): string {
  return `${lease.ip_address}-${lease.mac_address.replace(/:/g, '')}`
}

/**
 * Utility function to determine lease status
 * @param lease - The lease object from the API
 * @returns Status string for UI display
 */
export function getDhcpLeaseStatus(lease: DhcpLease): 'active' | 'expired' {
  if (!lease.is_active) return 'expired'
  
  const now = new Date()
  const leaseExpiration = new Date(lease.lease_time)
  return leaseExpiration > now ? 'active' : 'expired'
}

// Re-export generated hooks with cleaner names
export { 
  useLeasesQuery as useDhcpLeases,
  useHealthQuery as useHealthCheck,
  useStatusQuery as useApiStatus,
  apiKeys
} from './generated/queries'

// Re-export the api client
export { apiClient } from './client'
