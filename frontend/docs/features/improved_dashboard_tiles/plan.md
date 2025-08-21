# Improved Dashboard Tiles - Technical Plan

## Brief Description

The current front page statistics tiles show "Expiring Soon" (within 24 hours) and "New Devices" (last 24 hours) metrics, which are ineffective when DHCP leases are handed out for 24-hour durations. This makes these tiles essentially useless since all leases expire within 24 hours and all devices appear "new" daily. This plan redesigns the dashboard tiles to provide more meaningful insights for 24-hour lease environments.

## Current Implementation Analysis

### Existing Stats Cards (src/components/dhcp/stats-cards.tsx:64-77)
- **Total Leases**: Active DHCP assignments (useful)
- **Available IPs**: Remaining in pool (useful)
- **Expiring Soon**: Within 24 hours (useless with 24h leases)
- **New Devices**: Last 24 hours (useless with 24h leases)

### Current Logic Issues (src/lib/utils/stats-utils.ts:30-58)
- `calculateExpiringSoon()`: Shows leases expiring within 24 hours, but with 24-hour lease durations, this captures all active leases
- `calculateNewDevices()`: Shows unique MACs from last 24 hours, but with 24-hour leases, this shows all devices that renewed

### Data Structure Available
Based on backend analysis:
- `lease_time`: Lease expiration timestamp (not creation time)
- `is_active`: Boolean indicating if lease is currently active
- `is_static`: Boolean for static assignments
- `mac_address`: Unique device identifier
- `ip_address`: Assigned IP address
- `hostname`: Device hostname
- `vendor`: Device manufacturer from MAC lookup
- `pool_name`: DHCP pool assignment

## Proposed Improved Metrics

### Replace "Expiring Soon" with "Expiring Today"
Show leases expiring within the current day (0-24h from start of day), providing a more meaningful timeframe that indicates devices that may need renewal attention.

### Replace "New Devices" with "Device Types"
Count unique device vendors/manufacturers to show network diversity and device composition, providing insights into what types of devices are on the network.

### Alternative Option: "Recently Renewed"
If historical data becomes available, show devices that renewed their leases within the last few hours (2-4h window), indicating active network usage.

### Alternative Option: "Static vs Dynamic"
Show the ratio of static assignments vs dynamic leases, helping users understand their network configuration.

## Files and Functions to Modify

### Core Statistics Functions (src/lib/utils/stats-utils.ts)

**Functions to modify:**
- `calculateExpiringSoon(leases: DhcpLease[])`: Replace with `calculateExpiringToday(leases: DhcpLease[])`
  - Change logic to check if lease expires between now and end of current day
  - Use day boundaries instead of 24-hour rolling window

**Functions to add:**
- `calculateDeviceTypes(leases: DhcpLease[])`: Count unique vendors from active leases
  - Filter active leases, group by vendor, return count of unique vendors
  - Handle null/undefined vendor values gracefully

### Statistics Cards Component (src/components/dhcp/stats-cards.tsx)

**Lines to modify:**
- Line 44: Replace `calculateExpiringSoon(leases)` with `calculateExpiringToday(leases)`
- Line 45: Replace `calculateNewDevices(leases)` with `calculateDeviceTypes(leases)`
- Line 66-69: Update "Expiring Soon" card title and description
- Line 72-77: Update "New Devices" card title and description

**Specific changes:**
- Card title: "Expiring Soon" → "Expiring Today"
- Card description: "Within 24 hours" → "By end of day"
- Card title: "New Devices" → "Device Types"  
- Card description: "Last 24 hours" → "Unique manufacturers"

## Algorithm Details

### calculateExpiringToday Algorithm
```typescript
1. Get current date and calculate end of current day (23:59:59)
2. Filter active leases where lease_time falls between now and end of day
3. Return count of filtered leases
```

### calculateDeviceTypes Algorithm  
```typescript
1. Filter leases to only active leases
2. Extract vendor field from each lease
3. Filter out null/undefined/empty vendors
4. Create Set from vendor strings to get unique values
5. Return size of Set
```

## Implementation Phases

### Phase 1: Core Statistics Logic
1. Implement `calculateExpiringToday()` function in stats-utils.ts
2. Implement `calculateDeviceTypes()` function in stats-utils.ts  
3. Update existing function calls in stats-cards.tsx

### Phase 2: UI Updates
1. Update card titles and descriptions in StatsCards component
2. Test visual layout with new longer titles/descriptions
3. Ensure responsive behavior is maintained

### Phase 3: Validation and Testing
1. Test with various lease scenarios (all expiring today, mixed vendors, etc.)
2. Verify statistics update correctly with SSE real-time data
3. Test edge cases (no vendors, all static leases, empty pools)

## Success Criteria

1. "Expiring Today" tile shows meaningful data (not all leases) by using day boundaries
2. "Device Types" tile provides network composition insights instead of meaningless daily renewal counts
3. Tiles update in real-time via SSE connections
4. UI maintains consistent styling and responsive behavior
5. Statistics accurately reflect the current network state with 24-hour lease durations