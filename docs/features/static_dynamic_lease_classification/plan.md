# Static and Dynamic DHCP Lease Classification - Technical Plan

## Brief Description

Extend the existing DHCP leases endpoint (`/api/v1/leases`) with information that indicates whether each lease is a static or dynamic lease. The feature will read dnsmasq configuration files from the mounted config folder to identify static IP assignments defined via `dhcp-host` directives and classify all leases accordingly.

## Files and Functions to Create or Modify

### Files to Modify

1. **`app/models/dhcp_lease.py`**
   - Add `is_static: bool` field to `DhcpLease` class constructor
   - Update `to_dict()` method to include `is_static` field in JSON serialization

2. **`app/services/dhcp_service.py`**
   - Add `config_folder_path: str` parameter to `__init__()` method
   - Add `_static_leases_cache: Dict[str, Dict[str, str]]` instance variable for caching static lease definitions
   - Add `_load_static_leases()` method to parse dnsmasq configuration files
   - Add `_parse_dhcp_host_line()` method to parse individual dhcp-host configuration lines
   - Add `_is_static_lease()` method to check if a lease matches static configuration
   - Modify `_parse_lease_line()` method to determine static/dynamic status when creating `DhcpLease` objects

3. **`app/api/v1/dhcp_routes.py`**
   - Modify `get_dhcp_leases()` function to pass config folder path to `DhcpService` constructor
   - Add retrieval of `DHCP_CONFIG_FOLDER_PATH` from Flask configuration

### New Files to Create

None - all functionality will be integrated into existing files.

## Step-by-Step Algorithm Implementation

### 1. Static Lease Configuration Parsing Algorithm

**Method: `_load_static_leases()`**
1. Initialize empty dictionary to store static lease mappings
2. Read all files in the config folder following dnsmasq's default filtering rules:
   - Include all files except those ending with `~` (backup files)
   - Exclude files starting with `.` (hidden files)
   - Exclude files both starting and ending with `#` (commented out files)
3. For each valid configuration file:
   - Read file line by line
   - Skip empty lines and comments (lines starting with '#')
   - Look for lines containing 'dhcp-host=' directive
   - Call `_parse_dhcp_host_line()` to extract MAC and IP address
   - Store MAC-to-IP and IP-to-MAC mappings in cache dictionary
4. Log total number of static leases found

**Method: `_parse_dhcp_host_line()`**
1. Extract content after 'dhcp-host=' prefix
2. Split by commas to get components
3. Identify MAC address component (format: xx:xx:xx:xx:xx:xx or xx-xx-xx-xx-xx-xx)
4. Identify IP address component (format: xxx.xxx.xxx.xxx)
5. Return tuple of (normalized_mac_address, ip_address) or None if parsing fails

### 2. Lease Classification Algorithm

**Method: `_is_static_lease()`**
1. Check if MAC address exists in static leases cache
2. Check if IP address exists in static leases cache
3. If either MAC or IP matches static configuration, return True
4. Cross-validate that MAC and IP pair match expected static assignment
5. Return False if no static lease match found

**Modified Method: `_parse_lease_line()`**
1. Parse lease line using existing logic (timestamp, MAC, IP, hostname, client_id)
2. Call `_is_static_lease()` with extracted MAC and IP address
3. Create `DhcpLease` object with additional `is_static` parameter
4. Return populated lease object

### 3. Service Integration Algorithm

**Modified Method: `get_all_leases()`**
1. Check if static leases cache is populated, if not call `_load_static_leases()`
2. Proceed with existing lease file parsing logic
3. Each parsed lease will now include static/dynamic classification

## Implementation Phases

### Phase 1: Core Configuration Parsing
- Implement static lease configuration file parsing
- Add caching mechanism for static lease definitions
- Add unit tests for configuration parsing logic

### Phase 2: Lease Classification Integration
- Modify `DhcpLease` model to include `is_static` field
- Update `DhcpService` to determine static/dynamic status during parsing
- Modify API endpoint to pass config folder path

### Phase 3: Optimization and Error Handling
- Add comprehensive error handling for malformed configuration files
- Implement configuration file change detection and cache invalidation
- Add logging for static lease discovery and classification

## Technical Implementation Details

### Static Lease Detection Logic

The implementation will detect static leases through two approaches:

1. **Direct MAC Address Match**: Lease MAC address found in dhcp-host configuration
2. **IP Address Assignment Match**: Lease IP address is assigned to specific MAC in dhcp-host configuration

### Configuration File Discovery

The implementation will follow dnsmasq's default file filtering behavior when reading the config directory:
- **Include**: All regular files that don't match exclusion patterns
- **Exclude**: Files ending with `~` (backup files), files starting with `.` (hidden files), files both starting and ending with `#` (commented out configuration files)
- **Note**: Unlike some deployments that specify `*.conf` extension filtering, dnsmasq's default behavior reads all non-excluded files, allowing for flexible naming conventions

### dnsmasq Configuration Format Support

The parser will support standard dnsmasq dhcp-host directive formats:
- `dhcp-host=00:11:22:33:44:55,192.168.1.100`
- `dhcp-host=00:11:22:33:44:55,192.168.1.100,hostname`
- `dhcp-host=hostname,192.168.1.100`

### Caching Strategy

Static lease configurations will be loaded once during service initialization and cached in memory. The cache includes:
- MAC-to-IP mappings from dhcp-host directives  
- IP-to-MAC reverse mappings for efficient lookup
- Configuration file modification times for future cache invalidation

### Error Handling

- Graceful handling of missing or inaccessible configuration files
- Logging of malformed dhcp-host directives without failing entire parsing process
- Fallback behavior marking all leases as dynamic if configuration parsing fails
