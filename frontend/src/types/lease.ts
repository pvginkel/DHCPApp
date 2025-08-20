export type SortableField = 'ip_address' | 'mac_address' | 'hostname' | 'vendor' | 'lease_time' | 'is_active' | 'is_static'

export type SortDirection = 'asc' | 'desc' | 'none'

export interface SortConfig {
  field: SortableField | null
  direction: SortDirection
}

export interface FilterConfig {
  searchTerm: string
}