// Pool API client functions
import { useQuery, type UseQueryOptions } from '@tanstack/react-query'
import { API_BASE_URL } from './config'
import type { DhcpPool } from '@/types/pools'

// Manual API client for /pools endpoint (not in OpenAPI spec yet)
export async function fetchPools(): Promise<DhcpPool[]> {
  const response = await fetch(`${API_BASE_URL}/pools`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch pools: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
}

// TanStack Query hook for pools data
export function usePoolsQuery(
  options?: Omit<UseQueryOptions<DhcpPool[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['api', 'pools'] as const,
    queryFn: fetchPools,
    ...options,
  })
}