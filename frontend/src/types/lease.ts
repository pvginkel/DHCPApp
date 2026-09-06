export interface DhcpLease {
  ip_address: string
  mac_address: string
  hostname: string | null
  lease_time: string
  client_id: string | null
  is_active: boolean
  is_static: boolean
  pool_name: string | null
  vendor: string | null
}

export type SortableField = 'ip_address' | 'mac_address' | 'hostname' | 'vendor' | 'lease_time' | 'is_active' | 'is_static'

export type SortDirection = 'asc' | 'desc' | 'none'

export interface SortConfig {
  field: SortableField | null
  direction: SortDirection
}
