# MAC Address Vendor Display Feature - Technical Plan

## Description

Add a vendor column to the DHCP lease table that displays the device manufacturer/vendor based on MAC address OUI lookup. The backend has been extended with a `vendor` field that provides manufacturer information (e.g., "Apple, Inc.") derived from the MAC address prefix.

## Required File Changes

### Type Definitions
- **`src/types/lease.ts`** - Add `vendor` to the `SortableField` type to enable sorting by vendor name

### Sorting Logic
- **`src/lib/utils/lease-sorting.ts`** - Extend `getSortKey()` function to handle `vendor` field sorting with proper string comparison

### Table Component
- **`src/components/dhcp/lease-table.tsx`** - Add new vendor column to the table header and body:
  - Insert new `<TableHead>` with sortable button for "Vendor" column
  - Insert new `<TableCell>` displaying vendor information with proper formatting
  - Position vendor column after Hostname column for logical grouping
  - Handle null/empty vendor values with appropriate fallback display

### Generated API Types
- **No changes needed** - The `vendor` field is already available in the generated `DhcpLease` schema from the backend API

## Implementation Steps

### Step 1: Update Type Definitions
1. Add `'vendor'` to the `SortableField` union type in `src/types/lease.ts`

### Step 2: Extend Sorting Functionality
1. Add case for `'vendor'` in the `getSortKey()` function in `src/lib/utils/lease-sorting.ts`
2. Return lowercase vendor string for consistent sorting, handling null values appropriately

### Step 3: Update Table Display
1. Add vendor column header with sorting button in `src/components/dhcp/lease-table.tsx`
   - Insert after Hostname column (between existing columns 3 and 4)
   - Include sort icon and click handler following existing pattern
2. Add vendor data cell in table body
   - Display vendor name or "Unknown" placeholder for null values
   - Use consistent styling with other text columns
   - Apply muted text formatting for unknown/empty values

## Column Layout

The table will display columns in this order:
1. IP Address
2. MAC Address  
3. Hostname
4. **Vendor** (new)
5. Lease Expiration
6. Status

## Data Handling

- Backend provides `vendor?: string | null` field in DhcpLease schema
- Null/empty values display as "Unknown" with muted styling
- Vendor names sort alphabetically (case-insensitive)
- Column is fully sortable and searchable through existing filtering logic

## Technical Notes

- No API changes needed - vendor field already available in generated types after running `pnpm generate:api`
- No changes to generated code - only modify application-specific files
- Existing SSE update animations will work automatically with new column
- Search functionality will automatically include vendor field content
- Column width will auto-adjust based on content using existing table styling