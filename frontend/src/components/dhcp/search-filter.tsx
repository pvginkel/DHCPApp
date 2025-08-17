import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, X } from "lucide-react"
import type { FilterState } from "@/types/app"

interface SearchFilterProps {
  filterState: FilterState
  onFilterChange: (filters: Partial<FilterState>) => void
}

export function SearchFilter({ filterState, onFilterChange }: SearchFilterProps) {
  const handleSearchChange = (value: string) => {
    onFilterChange({ search: value })
  }

  const clearSearch = () => {
    onFilterChange({ search: '' })
  }

  return (
    <div className="flex items-center space-x-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <Input
          placeholder="Search leases..."
          value={filterState.search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-10 pr-10 w-64"
        />
        {filterState.search && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearSearch}
            className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  )
}
