import { useCallback } from 'react'
import { useLocalStorage } from '@/hooks/use-local-storage'
import { sortLeases } from '@/lib/utils/lease-sorting'
import type { components } from '@/lib/api/generated/types'
import type { SortableField, SortConfig } from '@/types/lease'

type DhcpLease = components['schemas']['DhcpLease']

const DEFAULT_SORT_CONFIG: SortConfig = {
  field: 'lease_time',
  direction: 'desc'
}

export function useLeaseSorting(leases: DhcpLease[]) {
  const [sortConfig, setSortConfig] = useLocalStorage<SortConfig>(
    'dhcp-lease-sort-config',
    DEFAULT_SORT_CONFIG
  )

  const handleSort = useCallback((field: SortableField) => {
    setSortConfig(current => {
      if (current.field === field) {
        // Cycle through: asc -> desc -> none
        switch (current.direction) {
          case 'asc':
            return { field, direction: 'desc' }
          case 'desc':
            return { field: null, direction: 'none' }
          case 'none':
            return { field, direction: 'asc' }
        }
      } else {
        // New field, start with ascending
        return { field, direction: 'asc' }
      }
    })
  }, [setSortConfig])

  const sortedLeases = sortLeases(leases, sortConfig)

  return {
    sortConfig,
    sortedLeases,
    handleSort
  }
}