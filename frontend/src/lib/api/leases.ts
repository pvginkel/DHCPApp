import { useQuery, type UseQueryOptions } from '@tanstack/react-query'
import { buildLoginUrl } from '@/lib/auth-redirect'
import type { DhcpLease } from '@/types/lease'

async function fetchLeases(): Promise<DhcpLease[]> {
  const response = await fetch('/api/dhcp/leases')

  if (response.status === 401) {
    window.location.href = buildLoginUrl()
    throw new Error('Redirecting to login')
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch leases: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export function useDhcpLeases(
  options?: Omit<UseQueryOptions<DhcpLease[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['dhcpLeases'] as const,
    queryFn: fetchLeases,
    ...options,
  })
}
