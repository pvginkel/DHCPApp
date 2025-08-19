# Simplified Event Stream - Technical Plan

## Description

Simplify the SSE event stream to send only change notifications instead of detailed change data. Frontend will receive a signal that data has changed and reload the full lease table data via the REST API. This removes complexity from the event system and ensures the fake changes system properly updates the in-memory lease cache.

## Current System Analysis

The current implementation sends detailed change events with full lease data:
- `LeaseUpdateEvent` model contains event type and full lease object
- SSE service detects specific changes (added, removed, updated, expired) 
- Events are broadcast with complete lease details in JSON format
- Fake changes system modifies leases but may not update main service cache consistently

## Files to be Modified

### Core Event System Changes

1. **app/services/sse_service.py:69-121** - `process_lease_change_notification()` and `broadcast_lease_events()`
   - Remove detailed change detection logic
   - Replace with simple "data_changed" notification broadcast
   - Ensure fake changes properly update DHCPService cache

2. **app/models/lease_update_event.py** - Remove or simplify this model
   - Replace with simple change notification structure
   - Remove lease-specific event details

3. **app/schemas/sse_schema.py** - Update SSE message schema
   - Replace detailed event schemas with simple notification schema

### Fake Changes System Fix

4. **app/services/sse_service.py:266-270** - `_get_fake_modified_leases()`
   - Ensure `set_modified_lease_data()` properly updates DHCPService internal state
   - Verify fake changes affect subsequent `get_all_leases()` calls

5. **app/services/dhcp_service.py** - Review cache management
   - Ensure `set_modified_lease_data()` integrates with `get_all_leases()`
   - Verify modified lease cache is used consistently

## Algorithm Changes

### New Simplified Flow
1. Receive lease change notification (file change or fake change trigger)
2. Update internal lease cache (from file or fake modifications)
3. Broadcast simple "data_changed" SSE event to all clients
4. Frontend receives notification and calls GET `/api/v1/leases` to reload data

### Event Message Format
Replace detailed events with:
```json
{
  "event_type": "data_changed",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

## Implementation Steps

1. **Simplify SSE event model** - Remove lease-specific event details
2. **Update SSE service** - Replace change detection with simple notification broadcast  
3. **Fix fake changes cache integration** - Ensure modified leases affect all subsequent reads
4. **Update API documentation** - Reflect simplified event format
5. **Test integration** - Verify fake changes work with simplified events

## Benefits

- Removes complexity from event detection and serialization
- Ensures frontend always has consistent view of current data
- Simplifies debugging and maintenance
- Fixes potential cache inconsistencies in fake changes system
- Frontend polling pattern is more reliable for data consistency