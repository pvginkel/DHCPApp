import type { components } from '@/lib/api/generated/types'
import { getLeaseStatus, getLeaseStatusDisplay } from '@/lib/utils/lease-utils'

type DhcpLease = components['schemas']['DhcpLease']

/**
 * Check if a lease matches the search term
 */
export function matchesSearchTerm(lease: DhcpLease, searchTerm: string): boolean {
  if (!searchTerm.trim()) {
    return true
  }
  
  const term = searchTerm.toLowerCase().trim()
  
  // Search in IP address
  if (lease.ip_address.toLowerCase().includes(term)) {
    return true
  }
  
  // Search in MAC address
  if (lease.mac_address.toLowerCase().includes(term)) {
    return true
  }
  
  // Search in hostname
  if (lease.hostname && lease.hostname.toLowerCase().includes(term)) {
    return true
  }
  
  // Search in vendor
  if (lease.vendor && lease.vendor.toLowerCase().includes(term)) {
    return true
  }
  
  // Search in status display text
  const status = getLeaseStatus(lease)
  const statusDisplay = getLeaseStatusDisplay(status)
  if (statusDisplay.label.toLowerCase().includes(term)) {
    return true
  }
  
  return false
}

/**
 * Filter leases based on search term
 */
export function filterLeases(leases: DhcpLease[], searchTerm: string): DhcpLease[] {
  if (!searchTerm.trim()) {
    return leases
  }
  
  return leases.filter(lease => matchesSearchTerm(lease, searchTerm))
}