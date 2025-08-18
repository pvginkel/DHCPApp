import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

export function formatLeaseExpiration(leaseTime: string): string {
  const date = new Date(leaseTime)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  
  if (diffMs <= 0) {
    return 'Expired'
  }
  
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (diffHours >= 24) {
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ${diffHours % 24}h`
  } else if (diffHours > 0) {
    return `${diffHours}h ${diffMinutes}m`
  } else {
    return `${diffMinutes}m`
  }
}

export function getLeaseStatus(lease: DhcpLease): 'active' | 'expired' | 'static' {
  if (lease.is_static) {
    return 'static'
  }
  return lease.is_active ? 'active' : 'expired'
}

export function getLeaseStatusDisplay(status: string): { label: string; className: string } {
  switch (status) {
    case 'active':
      return { label: 'Active', className: 'text-green-600' }
    case 'static':
      return { label: 'Static', className: 'text-blue-600' }
    case 'expired':
      return { label: 'Expired', className: 'text-red-600' }
    default:
      return { label: 'Unknown', className: 'text-gray-600' }
  }
}

export function formatMacAddress(macAddress: string): string {
  return macAddress.toUpperCase()
}