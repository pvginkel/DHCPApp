# Functional Stats Cards Implementation Plan

## Brief Description

Implement functional stats cards on the front page using the new backend DHCP pools endpoints. The four placeholder stats cards currently showing "--" values need to display real-time data: Total Leases, Available IPs, Expiring Soon, and New Devices. This requires integrating with the backend `/pools` endpoint and calculating metrics from both lease and pool data.

## Files and Functions to Create or Modify

### New Files to Create

1. **`src/types/pools.ts`** - Pool-related type definitions
   - `DhcpPool` interface matching backend response structure
   - Pool statistics calculation types

2. **`src/lib/api/pools.ts`** - Pool API client functions
   - `fetchPools()` function to call `/pools` endpoint
   - TanStack Query hooks for pools data

3. **`src/components/dhcp/stats-cards.tsx`** - Extract stats cards from homepage
   - Individual stat card components
   - Real-time data calculations
   - Loading and error states

4. **`src/lib/utils/stats-utils.ts`** - Statistics calculation utilities
   - `calculateTotalLeases()` function
   - `calculateAvailableIPs()` function  
   - `calculateExpiringSoon()` function
   - `calculateNewDevices()` function

### Files to Modify

1. **`src/routes/index.tsx`** - Homepage component
   - Replace placeholder stats cards with functional `<StatsCards />` component
   - Import and integrate new stats component

2. **`src/lib/api/client.ts`** - API client wrapper (if needed)
   - Add pools endpoint configuration if not auto-generated

## Step-by-Step Algorithm Implementation

### Phase 1: Pool Data Integration

1. **Pool Type Definition**
   - Define `DhcpPool` interface with properties:
     - `pool_name: string`
     - `start_ip: string`
     - `end_ip: string` 
     - `total_addresses: number`
     - `lease_duration: number`
     - `netmask: string`

2. **Pool API Client**
   - Create manual API client for `/pools` endpoint since it's not in OpenAPI spec
   - Implement TanStack Query hook `usePoolsQuery()`
   - Handle loading, error, and success states

### Phase 2: Statistics Calculation

1. **Total Leases Calculation**
   - Use existing lease data from `useLeasesQuery()`
   - Count all active leases (`is_active: true`)

2. **Available IPs Calculation**
   - Fetch pools data using `usePoolsQuery()`
   - For each pool: `total_addresses - active_leases_in_pool`
   - Sum available IPs across all pools
   - Match leases to pools using `pool_name` field

3. **Expiring Soon Calculation**
   - Filter active leases by `lease_time` within 24 hours
   - Convert ISO 8601 timestamps to Date objects
   - Count leases expiring before `Date.now() + 24 hours`

4. **New Devices Calculation**
   - Filter leases by `lease_time` created in last 24 hours
   - Identify unique devices by MAC address
   - Count distinct devices with recent lease times

### Phase 3: Component Implementation

1. **Stats Cards Component**
   - Extract existing placeholder cards from `index.tsx`
   - Create individual card components with props
   - Implement real-time data display
   - Add loading spinners and error states
   - Maintain existing Tailwind styling

2. **Real-time Updates**
   - Leverage existing TanStack Query caching and SSE updates
   - Ensure stats recalculate when lease data changes
   - Use React hooks for reactive updates

### Phase 4: Integration

1. **Homepage Integration**
   - Replace hardcoded stats cards with `<StatsCards />` component
   - Pass required data via props or context
   - Maintain existing layout and spacing

2. **Error Handling**
   - Handle pool endpoint failures gracefully
   - Show "--" values when data unavailable
   - Display error states consistently with existing patterns

## Implementation Phases

**Phase 1: Foundation (Pool API Integration)**
- Create pool types and API client
- Implement TanStack Query hooks for pools

**Phase 2: Statistics Engine** 
- Implement calculation utilities
- Create stats components with real data

**Phase 3: UI Integration**
- Replace placeholder cards with functional components
- Add loading and error states

**Phase 4: Testing and Polish**
- Verify real-time updates work correctly
- Test error scenarios and edge cases
- Ensure consistent styling and behavior