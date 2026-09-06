import { useQuery, type UseQueryOptions } from '@tanstack/react-query'
import { buildLoginUrl } from '@/lib/auth-redirect'
import type { DhcpPool } from '@/types/pools'

async function fetchPools(): Promise<DhcpPool[]> {
  const response = await fetch('/api/dhcp/pools')

  if (response.status === 401) {
    window.location.href = buildLoginUrl()
    throw new Error('Redirecting to login')
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch pools: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export function usePoolsQuery(
  options?: Omit<UseQueryOptions<DhcpPool[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['pools'] as const,
    queryFn: fetchPools,
    ...options,
  })
}
