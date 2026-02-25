import type { DhcpLease, SortableField, SortDirection, SortConfig } from '@/types/lease'

export function getSortKey(lease: DhcpLease, field: SortableField): string | number | Date {
  switch (field) {
    case 'ip_address':
      return lease.ip_address
        .split('.')
        .map(octet => parseInt(octet, 10).toString().padStart(3, '0'))
        .join('.')
    case 'mac_address':
      return lease.mac_address.toLowerCase()
    case 'hostname':
      return (lease.hostname || '').toLowerCase()
    case 'vendor':
      return (lease.vendor || '').toLowerCase()
    case 'lease_time':
      return new Date(lease.lease_time)
    case 'is_active':
      return lease.is_active ? 1 : 0
    case 'is_static':
      return lease.is_static ? 1 : 0
    default:
      throw new Error(`Unsupported sort field: ${field}`)
  }
}

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
    const collator = new Intl.Collator('en', {
      numeric: true,
      sensitivity: 'base'
    })
    comparison = collator.compare(String(aValue), String(bValue))
  }

  return direction === 'desc' ? -comparison : comparison
}

export function sortLeases(leases: DhcpLease[], sortConfig: SortConfig): DhcpLease[] {
  if (!sortConfig.field || sortConfig.direction === 'none') {
    return [...leases]
  }

  return [...leases].sort((a, b) =>
    compareLease(a, b, sortConfig.field!, sortConfig.direction)
  )
}
