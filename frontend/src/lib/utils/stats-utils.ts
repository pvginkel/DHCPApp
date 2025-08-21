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

// Calculate leases expiring by end of current day
export function calculateExpiringToday(leases: DhcpLease[]): number {
  const now = new Date()
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999)
  
  return leases.filter(lease => {
    if (!lease.is_active) return false
    
    const leaseTime = new Date(lease.lease_time).getTime()
    return leaseTime <= endOfDay.getTime() && leaseTime > now.getTime()
  }).length
}

// Calculate unique device types from all leases
export function calculateDeviceTypes(leases: DhcpLease[]): number {
  const uniqueVendors = new Set<string>()
  
  leases.forEach(lease => {
    if (lease.vendor && lease.vendor.trim() !== '') {
      uniqueVendors.add(lease.vendor)
    }
  })
  
  return uniqueVendors.size
}