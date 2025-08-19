// Statistics calculation utilities
import type { DhcpPool } from '@/types/pools'
import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

// Calculate total number of active leases
export function calculateTotalLeases(leases: DhcpLease[]): number {
  return leases.filter(lease => lease.is_active).length
}

// Calculate available IPs across all pools
export function calculateAvailableIPs(pools: DhcpPool[], leases: DhcpLease[]): number {
  let totalAvailable = 0
  
  for (const pool of pools) {
    // Count active leases in this specific pool
    const activeLeasesInPool = leases.filter(
      lease => lease.is_active && lease.pool_name === pool.pool_name
    ).length
    
    // Calculate available IPs in this pool
    const availableInPool = Math.max(0, pool.total_addresses - activeLeasesInPool)
    totalAvailable += availableInPool
  }
  
  return totalAvailable
}

// Calculate leases expiring within 24 hours
export function calculateExpiringSoon(leases: DhcpLease[]): number {
  const now = Date.now()
  const twentyFourHoursFromNow = now + (24 * 60 * 60 * 1000)
  
  return leases.filter(lease => {
    if (!lease.is_active) return false
    
    const leaseTime = new Date(lease.lease_time).getTime()
    return leaseTime <= twentyFourHoursFromNow && leaseTime > now
  }).length
}

// Calculate new devices (unique MACs) in the last 24 hours
export function calculateNewDevices(leases: DhcpLease[]): number {
  const now = Date.now()
  const twentyFourHoursAgo = now - (24 * 60 * 60 * 1000)
  
  // Get unique MAC addresses from leases created in the last 24 hours
  const recentDevices = new Set<string>()
  
  leases.forEach(lease => {
    const leaseTime = new Date(lease.lease_time).getTime()
    if (leaseTime >= twentyFourHoursAgo) {
      recentDevices.add(lease.mac_address)
    }
  })
  
  return recentDevices.size
}