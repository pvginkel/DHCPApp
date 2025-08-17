// Application-specific type definitions

export interface SortConfig<T = any> {
  key: keyof T | null
  direction: 'asc' | 'desc'
}

export interface FilterState {
  search: string
  deviceType?: string
  status?: 'active' | 'expired' | 'all'
}

export interface ColumnDef<T = any> {
  key: keyof T
  label: string
  sortable?: boolean
  className?: string
  render?: (value: any, item: T) => React.ReactNode
}

export interface TableProps<T = any> {
  data: T[]
  columns: ColumnDef<T>[]
  sortConfig: SortConfig<T>
  onSort: (key: keyof T) => void
  isLoading?: boolean
  emptyMessage?: string
}

// Component props
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

// Local storage keys
export const STORAGE_KEYS = {
  SORT_CONFIG: 'dhcp-table-sort-config',
  THEME: 'dhcp-app-theme',
} as const
