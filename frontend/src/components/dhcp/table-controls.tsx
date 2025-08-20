import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

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
  const handleClear = () => {
    onSearchChange('')
  }

  return (
    <div className="flex items-center justify-between gap-4 p-4 border-b border-border">
      <div className="flex items-center gap-2 flex-1 max-w-sm">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search leases..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
            aria-label="Search DHCP leases"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        {searchTerm && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleClear}
            aria-label="Clear search"
          >
            Clear
          </Button>
        )}
      </div>
      
      <div className="text-sm text-muted-foreground">
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