# SSE Push Updates Implementation Plan

## Brief Description

Implement Server-Sent Events (SSE) push updates to provide real-time DHCP lease notifications in the frontend. The implementation will establish a persistent SSE connection to the `/leases/stream` endpoint, handle incoming lease change events, update the lease table with visual flash animations, and make the "Live" label functional by reflecting the actual SSE connection status.

## Files and Functions to Create or Modify

### New Files
- `src/hooks/use-sse-connection.ts` - Custom hook for managing SSE connection lifecycle
- `src/lib/api/sse-client.ts` - SSE client implementation with event parsing and error handling
- `src/types/sse.ts` - TypeScript types for SSE events and connection state
- `src/lib/utils/sse-utils.ts` - Utility functions for SSE event parsing and validation

### Files to Modify
- `src/routes/index.tsx` - Update Live label to reflect actual SSE connection status
- `src/components/dhcp/lease-table.tsx` - Integrate SSE updates, implement visual flash animations for changed leases
- `src/lib/api/generated/queries.ts` - Add custom SSE query hook (currently commented out)

## Step-by-Step Implementation Algorithm

### 1. SSE Connection Management Hook (`use-sse-connection.ts`)
- Create custom hook with connection state: `'connecting' | 'connected' | 'disconnected' | 'error'`
- Implement EventSource lifecycle management with automatic reconnection logic
- Handle connection events: `onopen`, `onmessage`, `onerror`, `onclose`
- Provide methods: `connect()`, `disconnect()`, and `getConnectionStatus()`
- Include retry mechanism with exponential backoff for failed connections
- Track heartbeat events to detect connection health

### 2. SSE Client Implementation (`sse-client.ts`)
- Create SSE client class using native EventSource API
- Connect to `/leases/stream` endpoint with proper headers and configuration
- Parse incoming SSE events with data validation using Zod schemas
- Handle different event types: `lease-added`, `lease-updated`, `lease-removed`, `heartbeat`
- Implement proper error handling and connection recovery
- Provide event callbacks for different lease change types

### 3. Event Type Definitions (`sse.ts`)
- Define SSE connection state enum: `SSEConnectionState`
- Create interface for SSE event data structure matching backend event format
- Define lease change event types: `LeaseAddedEvent`, `LeaseUpdatedEvent`, `LeaseRemovedEvent`
- Create unified `SSEEvent` union type for all possible events
- Define connection status and error interfaces

### 4. SSE Utility Functions (`sse-utils.ts`)
- Implement event data parsing and validation functions
- Create lease comparison utilities to detect specific field changes
- Provide event type guards for type-safe event handling
- Include helper functions for connection status display formatting

### 5. Live Label Integration (`index.tsx`)
- Replace static green dot with dynamic connection status indicator
- Use `use-sse-connection` hook to get real-time connection state
- Display different colors/states: green (connected), yellow (connecting), red (disconnected/error)
- Update label text to reflect actual connection status
- Add tooltips showing detailed connection information

### 6. Lease Table SSE Integration (`lease-table.tsx`)
- Import and initialize SSE connection hook
- Set up event listeners for lease change notifications
- Implement TanStack Query cache invalidation on SSE events for both leases and stats
- Add visual flash animation system for updated lease rows
- Track lease changes and apply CSS animations for visual feedback
- Handle partial updates vs full data refreshes
- Implement fade-out animation for removed leases

### 7. Generated Query Hook Enhancement (`queries.ts`)
- Uncomment and implement the `useLeasesStreamQuery` function
- Create proper SSE hook that returns connection state and event data
- Integrate with existing TanStack Query patterns for consistency
- Provide proper TypeScript types for SSE hook return value

## Implementation Phases

### Phase 1: Core SSE Infrastructure
- Implement `use-sse-connection.ts` hook with basic connection management
- Create `sse-client.ts` with EventSource integration and event parsing
- Define TypeScript types in `sse.ts`
- Add utility functions in `sse-utils.ts`

### Phase 2: UI Integration
- Update Live label in `index.tsx` to use real connection status
- Integrate SSE hook into `lease-table.tsx` for real-time updates
- Implement cache invalidation on lease change events for both leases and stats queries

### Phase 3: Visual Enhancements
- Add flash animation system for updated lease table rows
- Implement visual feedback for lease additions, updates, and removals
- Polish connection status indicators and error states

### Phase 4: Error Handling and Reliability
- Implement robust error handling and reconnection logic
- Add connection health monitoring with heartbeat detection
- Enhance user feedback for connection issues and recovery

## Technical Implementation Details

### SSE Event Format (Backend Contract)
The backend sends events in this format:
```
event: lease-added|lease-updated|lease-removed|heartbeat
data: {"lease": {...}, "timestamp": "2024-01-01T00:00:00Z", "change_type": "added"}
```

### TanStack Query Integration
- Use `queryClient.invalidateQueries()` to refresh both lease and stats data on SSE events
- Invalidate stats queries (`status`, `pools`) when lease changes occur to update card values
- Maintain cache consistency between SSE updates and polling
- Implement optimistic updates for immediate UI feedback

### Visual Animation Requirements
- Flash animation on lease row updates with fade-out effect
- Different colors for different change types (green for added, blue for updated, red for removed)
- Smooth transitions that don't disrupt user interaction

### Connection Status Display
- Live label shows: "Live" (green), "Connecting..." (yellow), "Disconnected" (red)
- Tooltip provides detailed connection information and last event timestamp
- Graceful degradation when SSE is not available