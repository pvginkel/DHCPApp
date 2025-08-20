import type { components } from '@/lib/api/generated/types'
import type { SortableField, SortDirection, SortConfig } from '@/types/lease'

type DhcpLease = components['schemas']['DhcpLease']

/**
 * Get the sortable value from a lease for a specific field
 */
export function getSortKey(lease: DhcpLease, field: SortableField): string | number | Date {
  switch (field) {
    case 'ip_address':
      // Convert IP to numeric value for proper sorting
      return lease.ip_address
        .split('.')
        .map(octet => parseInt(octet, 10).toString().padStart(3, '0'))
        .join('.')
    case 'mac_address':
      return lease.mac_address.toLowerCase()
    case 'hostname':
      return (lease.hostname || '').toLowerCase()
    case 'lease_time':
      return new Date(lease.lease_time)
    case 'is_active':
      return lease.is_active ? 1 : 0
    case 'is_static':
      return lease.is_static ? 1 : 0
    default:
      return ''
  }
}

/**
 * Compare two leases for a specific field and direction
 */
export function compareLease(
  a: DhcpLease, 
  b: DhcpLease, 
  field: SortableField, 
  direction: SortDirection
): number {
  const aValue = getSortKey(a, field)
  const bValue = getSortKey(b, field)
  
  let comparison = 0
  
  if (aValue instanceof Date && bValue instanceof Date) {
    comparison = aValue.getTime() - bValue.getTime()
  } else if (typeof aValue === 'number' && typeof bValue === 'number') {
    comparison = aValue - bValue
  } else {
    // Use Intl.Collator for string comparisons with natural sorting
    const collator = new Intl.Collator('en', { 
      numeric: true, 
      sensitivity: 'base' 
    })
    comparison = collator.compare(String(aValue), String(bValue))
  }
  
  return direction === 'desc' ? -comparison : comparison
}

/**
 * Sort leases based on the given configuration
 */
export function sortLeases(leases: DhcpLease[], sortConfig: SortConfig): DhcpLease[] {
  if (!sortConfig.field || sortConfig.direction === 'none') {
    return [...leases]
  }
  
  return [...leases].sort((a, b) => 
    compareLease(a, b, sortConfig.field!, sortConfig.direction)
  )
}