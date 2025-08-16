# DHCP Leases REST Endpoint - Technical Plan

## Brief Description

Implement a REST API endpoint that returns all DHCP lease information from the dnsmasq leases file mounted in the containerized environment. The endpoint will read the DHCP lease file configured via environment variables and parse all lease entries to return comprehensive lease data in JSON format for frontend consumption.

## Files and Functions to Create or Modify

### New Files to Create

1. **`app/models/dhcp_lease.py`**
   - `DhcpLease` class: Model representing a single DHCP lease entry
   - `__init__()`: Initialize lease with IP, MAC, hostname, start/end times, binding state
   - `to_dict()`: Convert lease object to dictionary for JSON serialization
   - `is_active()`: Determine if lease is currently active based on end time

2. **`app/services/dhcp_service.py`**
   - `DhcpService` class: Service for reading and parsing DHCP lease files
   - `__init__()`: Initialize with lease file path from configuration
   - `get_all_leases()`: Read lease file and return list of DhcpLease objects
   - `parse_lease_file()`: Parse dnsmasq lease file format
   - `_parse_lease_line()`: Parse individual lease line into DhcpLease object

3. **`app/api/v1/dhcp_routes.py`**
   - `get_dhcp_leases()`: REST endpoint handler for `/leases` route
   - Error handling for file access issues and parsing errors

### Files to Modify

1. **`app/api/v1/__init__.py`**
   - Import and register dhcp_routes module

2. **`app/utils/__init__.py`**
   - Refactor `ResponseHelper` class to follow REST API best practices
   - Remove `success` and `message` wrapper attributes
   - Create methods for direct data responses and proper error responses

3. **`app/api/v1/routes.py`**
   - Update existing endpoints to use refactored ResponseHelper methods

4. **`requirements.txt`**
   - Add dependency for lease file parsing (if needed)

## Algorithm Details

### DHCP Lease File Parsing Algorithm

The dnsmasq lease file format follows this structure per line:
```
<timestamp> <mac_address> <ip_address> <hostname> <client_id>
```

1. **File Reading Process:**
   - Open lease file from `DHCP_LEASE_FILE_PATH` configuration
   - Read all lines from file
   - Skip empty lines and comments
   - Parse each valid line into lease components

2. **Lease Parsing Logic:**
   - Split each line by whitespace into components
   - Extract timestamp (Unix timestamp format)
   - Extract MAC address (format: aa:bb:cc:dd:ee:ff)
   - Extract IP address (IPv4 format: xxx.xxx.xxx.xxx)
   - Extract hostname (may be * if unknown)
   - Extract client ID (optional, may be * if not provided)

3. **Data Transformation:**
   - Convert Unix timestamp to ISO 8601 format for API response
   - Validate IP address format
   - Normalize MAC address format
   - Handle missing or unknown hostnames
   - Determine lease status (active/expired) based on timestamp

### API Response Structure

**Success Response (HTTP 200):**
```json
[
  {
    "ip_address": "192.168.1.100",
    "mac_address": "aa:bb:cc:dd:ee:ff",
    "hostname": "device-name",
    "lease_time": "2024-01-15T10:30:00Z",
    "client_id": "client-identifier",
    "is_active": true
  }
]
```

**Error Response (HTTP 500):**
```json
{
  "error": "Unable to read DHCP lease file",
  "details": "File not found: /var/lib/dhcp/dhcpd.leases"
}
```

## Implementation Phases

### Phase 1: ResponseHelper Refactor (Breaking Change)
- Refactor `ResponseHelper` class in `app/utils/__init__.py` to remove `success` and `message` wrapper attributes
- Create new methods: `data_response()` for direct data returns and `error_response()` for structured error responses
- Update existing endpoints in `app/api/v1/routes.py` to use refactored ResponseHelper
- Ensure all responses follow REST API best practices with proper HTTP status codes

### Phase 2: Core Data Models and Services
- Create `DhcpLease` model class with all required fields
- Implement `DhcpService` with file reading and parsing capabilities
- Add comprehensive error handling for file access issues

### Phase 3: REST API Endpoint
- Create `/api/v1/leases` GET endpoint in `dhcp_routes.py`
- Integrate with `DhcpService` to retrieve lease data
- Return direct JSON array for success cases (HTTP 200)
- Return structured error objects for failure cases (HTTP 500, etc.)
- Add logging for debugging and monitoring

### Phase 4: Integration and Testing
- Register new routes with Flask blueprint
- Update requirements.txt with any new dependencies
- Verify endpoint functionality with sample lease files
- Test error handling scenarios (missing file, corrupt data, etc.)
- Validate that all endpoints follow REST API best practices

## Configuration Requirements

The endpoint will use the existing `DHCP_LEASE_FILE_PATH` environment variable from the configuration system to locate the dnsmasq lease file. No additional configuration changes are required as the file path is already configured in the `Config` class.

## Error Handling Strategy

- **File Not Found:** Return HTTP 500 with structured error response containing error message and details
- **Parse Errors:** Log parsing issues and skip invalid lines, continue processing valid entries
- **Empty File:** Return HTTP 200 with empty JSON array `[]`
- **Invalid File Format:** Return HTTP 500 with structured error response if file format is completely unrecognizable
- **Permission Errors:** Return HTTP 500 with appropriate error message for file access permission issues

## REST API Best Practices Implementation

### ResponseHelper Refactor Details

The current `ResponseHelper` class wraps all responses in `success` and `message` attributes, which violates REST principles. The refactor will:

1. **Remove wrapper attributes:** Eliminate `success` and `message` from response bodies
2. **Use HTTP status codes:** Let HTTP status codes indicate success (2xx) or failure (4xx/5xx)
3. **Direct data responses:** Return actual data directly for successful operations
4. **Structured error responses:** Use consistent error object format for failures

### New ResponseHelper Methods

- `data_response(data)`: Returns data directly without wrapper (for HTTP 2xx responses)
- `error_response(message, details=None)`: Returns structured error object (for HTTP 4xx/5xx responses)

## Dependencies

No additional external dependencies are required. The implementation will use only Python standard library modules for file I/O and datetime handling, maintaining the project's minimal dependency approach.
