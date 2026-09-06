import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useSseContext } from '@/contexts/sse-context'

/**
 * Subscribes to 'data_changed' SSE events and invalidates DHCP-related queries.
 * Uses the template's SSE context (SharedWorker-based) instead of a custom EventSource.
 */
export function useDataChangeSse() {
  const { addEventListener, isConnected } = useSseContext()
  const queryClient = useQueryClient()

  useEffect(() => {
    const unsubscribe = addEventListener('data_changed', () => {
      queryClient.invalidateQueries({ queryKey: ['dhcpLeases'] })
      queryClient.invalidateQueries({ queryKey: ['pools'] })
    })

    return unsubscribe
  }, [addEventListener, queryClient])

  return { isConnected }
}
