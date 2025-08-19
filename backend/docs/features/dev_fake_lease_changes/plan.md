# Development Mode Fake Lease Changes - Technical Plan

## Brief Description

Implement functionality to simulate DHCP lease changes in development mode for testing SSE (Server-Sent Events) functionality. When the `/api/v1/internal/notify-lease-change` endpoint is called in development mode, it should make small alterations to the loaded lease data instead of just re-reading the actual lease file. This allows testing of the SSE streaming functionality without requiring actual DHCP lease file changes.

## Files and Functions to be Created or Modified

### New Files
- `app/services/dev_lease_modifier.py` - Service class for applying fake lease modifications in development mode

### Modified Files

#### `app/services/sse_service.py`
- `process_lease_change_notification()` - Add development mode detection and call to dev lease modifier
- Add import for dev lease modifier service
- Add development mode flag detection logic

#### `app/services/dhcp_service.py` 
- `get_all_leases()` - Add optional parameter to return modified leases in development mode
- Add method to set modified lease data cache
- Add import for development mode detection

#### `config.py`
- Add `DEV_FAKE_LEASE_CHANGES: bool` configuration flag to DevelopmentConfig class

## Step-by-Step Algorithm for Fake Lease Modifications

### Development Lease Modifier Service (`DevLeaseModifier`)

1. **Initialize with base lease data**: Store the original lease data as the baseline
2. **Apply random modifications**: When `modify_leases()` is called, apply one of these changes:
   - **Add a lease**: Generate a fake lease with random IP in pool range, random MAC, hostname like "test-device-N"
   - **Remove a lease**: Randomly select and remove an existing dynamic lease (never remove static leases)
   - **Modify lease expiration**: Change expiration time of existing lease (±30 minutes to 2 hours)
   - **Change hostname**: Update hostname of existing lease to "modified-hostname-N"

3. **Ensure realistic changes**: 
   - Only modify dynamic leases, never static assignments
   - Keep MAC addresses in valid format (xx:xx:xx:xx:xx:xx)
   - Ensure added IP addresses fall within configured DHCP pool ranges
   - Maintain lease file timestamp format consistency

4. **Rotation logic**: Cycle through different modification types to provide varied test scenarios

### SSE Service Integration

1. **Development mode detection**: Check if `app.config['FLASK_ENV'] == 'development'` and `app.config.get('DEV_FAKE_LEASE_CHANGES', True)`
2. **Conditional processing**: In `process_lease_change_notification()`:
   - If development mode with fake changes enabled: Call `dev_lease_modifier.modify_leases()` and use modified data
   - If production mode: Use normal `dhcp_service.get_all_leases()` flow
3. **Cache management**: Ensure modified lease data properly updates the SSE service's cached lease state

### DHCP Service Integration

1. **Modified data injection**: Add `set_modified_lease_data(leases: List[DhcpLease])` method
2. **Conditional data source**: In `get_all_leases()`, add optional `use_modified_data: bool = False` parameter
3. **Data precedence**: When `use_modified_data=True`, return modified lease cache instead of reading from file

## Implementation Phases

### Phase 1: Core Infrastructure
- Create `DevLeaseModifier` service class
- Add configuration flag to `DevelopmentConfig`
- Implement basic lease addition/removal functionality

### Phase 2: SSE Integration  
- Modify `SseService.process_lease_change_notification()` for development mode detection
- Integrate dev modifier with lease change processing
- Update `DhcpService` to support modified data injection

### Phase 3: Advanced Modifications
- Implement lease expiration time changes
- Add hostname modification functionality  
- Add rotation logic for different modification types

### Phase 4: Testing and Validation
- Verify SSE events are properly generated for each modification type
- Test that only development mode enables fake changes
- Ensure production mode behavior remains unchanged