import { Search, X } from 'lucide-react'

interface TableControlsProps {
  searchTerm: string
  onSearchChange: (value: string) => void
  totalCount: number
  filteredCount: number
}

export function TableControls({
  searchTerm,
  onSearchChange,
  totalCount,
  filteredCount
}: TableControlsProps) {
  return (
    <div className="flex items-center justify-between gap-4 p-4 border-b border-border" data-testid="table-controls">
      <div className="flex items-center gap-2 flex-1 max-w-sm">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search leases..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-9 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            aria-label="Search DHCP leases"
            data-testid="lease-search-input"
          />
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
            aria-hidden="true"
          />
        </div>
        {searchTerm && (
          <button
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-3"
            onClick={() => onSearchChange('')}
            aria-label="Clear search"
            data-testid="lease-search-clear"
          >
            <X className="h-4 w-4 mr-1" />
            Clear
          </button>
        )}
      </div>

      <div className="text-sm text-muted-foreground" data-testid="lease-count">
        {searchTerm ? (
          <>
            Showing {filteredCount} of {totalCount} leases
          </>
        ) : (
          <>
            {totalCount} lease{totalCount !== 1 ? 's' : ''}
          </>
        )}
      </div>
    </div>
  )
}
