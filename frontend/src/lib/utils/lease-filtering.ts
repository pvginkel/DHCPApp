import type { DhcpLease } from '@/types/lease'
import { getLeaseStatus, getLeaseStatusDisplay } from '@/lib/utils/lease-utils'

function matchesSearchTerm(lease: DhcpLease, searchTerm: string): boolean {
  if (!searchTerm.trim()) {
    return true
  }

  const term = searchTerm.toLowerCase().trim()

  if (lease.ip_address.toLowerCase().includes(term)) {
    return true
  }

  if (lease.mac_address.toLowerCase().includes(term)) {
    return true
  }

  if (lease.hostname && lease.hostname.toLowerCase().includes(term)) {
    return true
  }

  if (lease.vendor && lease.vendor.toLowerCase().includes(term)) {
    return true
  }

  const status = getLeaseStatus(lease)
  const statusDisplay = getLeaseStatusDisplay(status)
  if (statusDisplay.label.toLowerCase().includes(term)) {
    return true
  }

  return false
}

export function filterLeases(leases: DhcpLease[], searchTerm: string): DhcpLease[] {
  if (!searchTerm.trim()) {
    return leases
  }

  return leases.filter(lease => matchesSearchTerm(lease, searchTerm))
}
