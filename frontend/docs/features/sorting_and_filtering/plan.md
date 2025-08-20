# DHCP Lease Table Sorting and Filtering Implementation Plan

## Brief Description

Implementation of multi-column sorting and live search functionality for the DHCP lease table. The sorting functionality must support all table columns with persistent preferences stored in localStorage, while search provides real-time filtering that is session-based only (not persisted).

## Key Requirements from Product Brief

- **Multi-column Sorting**: All table columns sortable with lease expiration as default sort order
- **Persistent Sort Preferences**: User's selected sort order saved in browser storage
- **Live Search Functionality**: Real-time filtering of lease data (session-based, not persisted)
- **Visual Flash Animations**: Maintain existing visual feedback for data changes via SSE
- **Functional Programming**: Use functional programming exclusively with no OOP patterns

## Files and Functions to Create or Modify

### New Files to Create

1. **`src/hooks/use-lease-sorting.ts`**
   - Custom hook for managing sort state and logic
   - Functions: `useLeaseSorting()` returning sort state and handlers
   - Integration with localStorage for persistence

2. **`src/hooks/use-lease-filtering.ts`** 
   - Custom hook for managing search/filter state
   - Functions: `useLeaseFiltering()` returning filter state and handlers
   - Session-based filtering (no localStorage persistence)

3. **`src/lib/utils/lease-sorting.ts`**
   - Pure functions for lease data sorting logic
   - Functions: `sortLeases()`, `getSortKey()`, `compareLease()`
   - Support for all DhcpLease properties with type-safe comparisons

4. **`src/lib/utils/lease-filtering.ts`**
   - Pure functions for lease data filtering logic
   - Functions: `filterLeases()`, `matchesSearchTerm()`
   - Search across IP address, MAC address, hostname, and status

5. **`src/components/dhcp/table-controls.tsx`**
   - Component containing search input and sort controls
   - Functions: Search input component, sort direction indicators
   - Clean, accessible UI following existing design patterns

### Files to Modify

1. **`src/components/dhcp/lease-table.tsx`**
   - Integrate sorting and filtering hooks
   - Add TableControls component above the table
   - Apply sorting and filtering to displayLeases before rendering
   - Modify table headers to include clickable sort controls
   - Preserve existing SSE animation logic and flash effects

2. **`src/types/lease.ts`** (create if needed)
   - Add TypeScript interfaces for sort and filter states
   - Types: `SortConfig`, `FilterConfig`, `SortDirection`, `SortableField`

## Detailed Implementation Steps

### Phase 1: Core Sorting Infrastructure

1. **Create sorting utilities** (`src/lib/utils/lease-sorting.ts`):
   - `sortLeases(leases: DhcpLease[], sortConfig: SortConfig): DhcpLease[]`
   - `getSortKey(lease: DhcpLease, field: SortableField): string | number | Date`
   - `compareLease(a: DhcpLease, b: DhcpLease, field: SortableField, direction: SortDirection): number`
   - Use `Intl.Collator` with `numeric: true` option for natural sorting of all string fields
   - Support sorting by: ip_address, mac_address, hostname, lease_time, is_active, is_static

2. **Create sorting hook** (`src/hooks/use-lease-sorting.ts`):
   - Use `useLocalStorage` hook for persistence
   - Default sort: lease_time descending (lease expiration as specified)
   - Return: `{ sortConfig, setSortConfig, sortedLeases }`
   - Handle sort direction toggle (asc/desc/none)

3. **Create type definitions** (`src/types/lease.ts`):
   ```typescript
   type SortableField = 'ip_address' | 'mac_address' | 'hostname' | 'lease_time' | 'is_active' | 'is_static'
   type SortDirection = 'asc' | 'desc' | 'none'
   interface SortConfig {
     field: SortableField | null
     direction: SortDirection
   }
   ```

### Phase 2: Search/Filtering Infrastructure  

1. **Create filtering utilities** (`src/lib/utils/lease-filtering.ts`):
   - `filterLeases(leases: DhcpLease[], searchTerm: string): DhcpLease[]`
   - `matchesSearchTerm(lease: DhcpLease, searchTerm: string): boolean`
   - Search across: ip_address, mac_address, hostname, lease status display text
   - Case-insensitive search with trimmed input

2. **Create filtering hook** (`src/hooks/use-lease-filtering.ts`):
   - Use regular `useState` (session-based, no persistence)
   - Return: `{ searchTerm, setSearchTerm, filteredLeases }`
   - Real-time filtering with debouncing for performance

### Phase 3: UI Components

1. **Create table controls component** (`src/components/dhcp/table-controls.tsx`):
   - Search input with clear button and search icon
   - Results count display
   - Accessible labels and keyboard navigation
   - Styling consistent with existing Tailwind/Radix patterns

2. **Modify table headers** in `lease-table.tsx`:
   - Add clickable sort buttons to each column header
   - Visual indicators for current sort field and direction (arrows/icons)
   - Accessible sort controls with proper ARIA labels

### Phase 4: Integration

1. **Update LeaseTable component**:
   - Import and use both sorting and filtering hooks
   - Apply sorting first, then filtering to the lease data
   - Add TableControls component above the table
   - Ensure SSE animations work with sorted/filtered data
   - Maintain existing loading, error, and empty states

2. **Data flow**:
   ```
   Raw leases → Sort → Filter → Display leases → Render with animations
   ```

## Algorithm Details

### Sorting Algorithm
- **Multi-field support**: Each column maps to a DhcpLease property
- **Type-aware comparison**: String, number, Date, and boolean comparisons
- **Natural sorting**: All string fields use `Intl.Collator` with `numeric: true` for proper numeric sorting
- **Case-insensitive**: Use `Intl.Collator` with `sensitivity: 'base'` for case-insensitive comparison
- **Default behavior**: lease_time descending for "most urgent first" ordering
- **Stable sort**: Maintains consistent ordering for equal values
- **Three-state sort**: ascending → descending → none (original order)

### Filtering Algorithm  
- **Multi-field search**: Search across IP, MAC, hostname, and computed status
- **Substring matching**: Case-insensitive partial matches
- **Real-time updates**: Filter applies on every keystroke
- **Performance optimized**: Early returns and efficient string operations

### Data Integration
- **Sort first, filter second**: Apply sorting to raw data, then filter sorted results
- **Animation preservation**: Maintain lease key consistency for SSE flash animations
- **State isolation**: Sort and filter states managed independently with separate hooks

## Key Technical Considerations

1. **Performance**: Sorting and filtering operations run on every data update and user interaction
2. **Animation compatibility**: Ensure lease keys remain stable for SSE flash animations
3. **Accessibility**: All interactive elements must be keyboard navigable with proper ARIA labels
4. **Type safety**: Full TypeScript coverage for all new interfaces and functions
5. **State persistence**: Only sorting preferences persist; search state is session-based
6. **Functional style**: All code follows functional programming patterns with pure functions
7. **Natural sorting**: Use browser's native `Intl.Collator` API for proper numeric sorting
8. **Case insensitive**: All string comparisons are case-insensitive via `Intl.Collator`

## Testing Considerations

- Test sorting behavior with various data types and edge cases
- Verify localStorage persistence and retrieval of sort preferences
- Test search functionality across all searchable fields
- Ensure SSE animations continue working with sorted/filtered data
- Validate accessibility features with keyboard navigation