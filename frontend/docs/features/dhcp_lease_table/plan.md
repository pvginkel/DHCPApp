# DHCP Lease Table Implementation Plan

## Brief Description

Implement the basic DHCP lease table feature as the core functionality of the DHCP Monitoring Frontend. This initial implementation displays DHCP lease information in a simple table format using the existing backend API. Future phases will add sorting, search, and real-time updates via Server-Sent Events (SSE).

## Files and Functions to Create/Modify

### New Components to Create

**`src/components/dhcp/lease-table.tsx`**
- Main DHCP lease table component
- Integrates with backend API using `useLeasesQuery` hook
- Displays basic table with columns: IP address, MAC address, hostname, lease expiration, status
- Uses existing Table UI components from `src/components/ui/table.tsx`
- Shows loading and error states

**`src/lib/utils/lease-utils.ts`**
- Basic utility functions for lease data processing
- Format lease expiration times for display
- Calculate lease status (active, expired)
- Basic data formatting functions

### Files to Modify

**`src/routes/index.tsx`**
- Replace placeholder content with actual DHCP lease table
- Remove loading spinner placeholder
- Integrate `LeaseTable` component
- Keep placeholder stats for future implementation

## Algorithm Details

### Basic Data Display
1. Use `useLeasesQuery` hook to fetch lease data from `/leases` endpoint
2. Display loading state while data is being fetched
3. Show error state if API request fails
4. Render lease data in table format with proper formatting

## Data Flow

1. **Initial Load**: `useLeasesQuery` fetches initial lease data from `/leases` endpoint
2. **Data Processing**: `lease-utils` functions format lease data for display
3. **Display**: `LeaseTable` renders lease data in a basic table format
4. **Error Handling**: Show appropriate error states for failed API calls

## Implementation Steps

### Current Phase: Basic Table Display
1. Create `lease-utils.ts` with basic formatting functions
2. Create `LeaseTable` component with:
   - Basic table structure using existing UI components
   - Integration with `useLeasesQuery` hook
   - Loading and error states
   - Columns: IP Address, MAC Address, Hostname, Lease Expiration, Status
3. Update `index.tsx` to use `LeaseTable` component
4. Remove placeholder loading spinner
5. Test basic functionality with backend API

### Future Phases (Not Implemented Yet)
- **Phase 2**: Add sorting functionality with localStorage persistence
- **Phase 3**: Add search/filtering capabilities
- **Phase 4**: Implement real-time updates via SSE
- **Phase 5**: Add statistics dashboard and visual enhancements