import type { DhcpPool } from '@/types/pools'
import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

export function calculateTotalLeases(leases: DhcpLease[]): number {
  return leases.filter(lease => lease.is_active).length
}

export function calculateAvailableIPs(pools: DhcpPool[], leases: DhcpLease[]): number {
  let totalAvailable = 0

  for (const pool of pools) {
    const activeLeasesInPool = leases.filter(
      lease => lease.is_active && lease.pool_name === pool.pool_name
    ).length

    const availableInPool = Math.max(0, pool.total_addresses - activeLeasesInPool)
    totalAvailable += availableInPool
  }

  return totalAvailable
}

export function calculateExpiringToday(leases: DhcpLease[]): number {
  const now = new Date()
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999)

  return leases.filter(lease => {
    if (!lease.is_active) return false

    const leaseTime = new Date(lease.lease_time).getTime()
    return leaseTime <= endOfDay.getTime() && leaseTime > now.getTime()
  }).length
}

export function calculateDeviceTypes(leases: DhcpLease[]): number {
  const uniqueVendors = new Set<string>()

  leases.forEach(lease => {
    if (lease.vendor && lease.vendor.trim() !== '') {
      uniqueVendors.add(lease.vendor)
    }
  })

  return uniqueVendors.size
}
