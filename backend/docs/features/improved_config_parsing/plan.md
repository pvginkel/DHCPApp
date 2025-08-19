# Improved dnsmasq Configuration Parsing Technical Plan

## Brief Description

Refactor dnsmasq configuration parsing to use a single dnsmasq.conf file path instead of separate lease file and config folder paths. The application should automatically discover configuration directories, extensions, lease files, and DNS pools from the main configuration file. Additionally, expose all DNS pools with usage statistics showing available and in-use addresses per pool.

## Files and Functions to be Created or Modified

### Configuration Changes
- **config.py**: Replace `DHCP_LEASE_FILE_PATH` and `DHCP_CONFIG_FOLDER_PATH` with single `DNSMASQ_CONFIG_FILE_PATH`
- **.env.example**: Update environment variable from separate paths to single `DNSMASQ_CONFIG_FILE_PATH`

### Service Layer Changes
- **app/services/dhcp_service.py**: Major refactor of `DhcpService` class
  - Modify `__init__()` to accept single config file path
  - Add `_parse_main_config()` method to extract lease file path and config directories
  - Add `_discover_config_files()` method to find config files with proper extensions
  - Add `_parse_dhcp_ranges()` method to extract DHCP pool information
  - Add `get_dns_pools()` method to return pool information
  - Add `get_pool_usage_statistics()` method to calculate usage per pool
  - Update `_load_static_leases()` to use discovered config directories and extensions

### Model Changes
- **app/models/dhcp_pool.py** (new): Create DhcpPool model for representing DNS pools
- **app/models/dhcp_lease.py**: Add pool_name field to track which pool a lease belongs to

### Schema Changes
- **app/schemas/dhcp_pool_schema.py** (new): Marshmallow schema for DhcpPool serialization
- **app/schemas/dhcp_lease_schema.py**: Update to include pool_name field

### API Changes
- **app/api/v1/dhcp_routes.py**: Add new endpoints for pool information and usage statistics
- **app/api/v1/routes.py**: Register new pool-related routes

### Application Bootstrap
- **app.py**: Update DhcpService initialization to use single config path

### Testing Infrastructure
- **requirements.txt**: Add pytest and pytest-cov for testing framework
- **test/test_dhcp_service.py** (new): Comprehensive unit tests for DhcpService
- **test/test_config_parsing.py** (new): Tests for configuration file parsing
- **test/test_pool_detection.py** (new): Tests for DHCP pool detection and usage calculation
- **test/fixtures/** (new): Test data fixtures based on existing data/ folder samples

## Algorithm Details

### Main Configuration Parsing Algorithm
1. Read the main dnsmasq.conf file specified by `DNSMASQ_CONFIG_FILE_PATH`
2. Parse `dhcp-leasefile=` directive to extract lease file path
3. Parse `conf-dir=` directives to extract:
   - Directory paths
   - File extension patterns (e.g., `*.conf`)
4. Store discovered paths and patterns for later use

### Configuration File Discovery Algorithm
1. For each discovered config directory:
   - List all files in the directory
   - Apply extension filtering based on parsed patterns
   - Apply dnsmasq's default filtering rules (exclude ~, ., #...# files)
   - Return filtered list of configuration files

### DHCP Pool Parsing Algorithm
1. Read all discovered configuration files
2. Parse `dhcp-range=` directives to extract:
   - Set/tag name (pool identifier)
   - Start IP address
   - End IP address  
   - Netmask
   - Lease duration
3. Calculate total addresses per pool: `end_ip - start_ip + 1`
4. Create DhcpPool objects with parsed information

### Pool Usage Statistics Algorithm
1. For each discovered pool:
   - Count active leases within the pool's IP range
   - Calculate: `used_addresses = count_of_active_leases_in_range`
   - Calculate: `available_addresses = total_addresses - used_addresses`
   - Calculate: `usage_percentage = (used_addresses / total_addresses) * 100`

## Implementation Phases

### Phase 1: Configuration Discovery
- Implement main config file parsing
- Add lease file and config directory discovery
- Update configuration classes and environment variables

### Phase 2: Pool Detection and Modeling
- Create DhcpPool model and schema
- Implement DHCP range parsing from config files
- Add pool identification logic

### Phase 3: Usage Statistics
- Implement pool usage calculation
- Update lease parsing to include pool association
- Add new API endpoints for pool information

### Phase 4: Comprehensive Testing
- Add pytest testing framework to requirements
- Create test fixtures based on existing data/ folder samples
- Implement unit tests for all new parsing functionality:
  - Main config parsing (dnsmasq.conf)
  - Config directory and extension discovery  
  - DHCP pool detection from dhcp-range directives
  - Pool usage statistics calculation
  - Static lease detection across multiple config files
- Validate against existing sample files:
  - `/data/dnsmasq.conf` (main config with conf-dir directives)
  - `/data/dnsmasq.leases` (sample lease data)
  - `/data/dnsmasq.d/` configs (DHCP ranges and options)
  - `/data/dnsmasq-static-generated.d/` configs (static host assignments)

### Phase 5: Integration and Deployment
- Update service initialization throughout application
- Verify backward compatibility where possible
- Run full test suite against sample data