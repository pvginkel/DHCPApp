import { useState, useMemo } from 'react'
import { filterLeases } from '@/lib/utils/lease-filtering'
import type { components } from '@/lib/api/generated/types'

type DhcpLease = components['schemas']['DhcpLease']

export function useLeaseFiltering(leases: DhcpLease[]) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredLeases = useMemo(() => {
    return filterLeases(leases, searchTerm)
  }, [leases, searchTerm])

  return {
    searchTerm,
    setSearchTerm,
    filteredLeases
  }
}