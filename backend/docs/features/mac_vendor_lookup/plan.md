# MAC Address Vendor Lookup Feature - Technical Plan

## Brief Description

Add MAC address vendor identification functionality to the DHCP monitoring application to return the device manufacturer/vendor based on the MAC address OUI (Organizationally Unique Identifier) prefix. This will enhance device identification capabilities by showing which company manufactured each network device based on its MAC address.

## Dependencies

### Python Package Requirement
- **`mac-vendor-lookup`** - Third-party PyPI package that provides local IEEE OUI database and lookup functionality
- Installation: `pip install mac-vendor-lookup`
- Features: Local OUI database, automatic updates, simple API

## Files and Functions to be Created or Modified

### New Files to Create

1. **`app/services/mac_vendor_service.py`**
   - `MacVendorService` class with vendor lookup functionality
   - `get_vendor(mac_address: str) -> Optional[str]` method
   - Uses `mac-vendor-lookup` package internally
   - Simple error handling for lookup failures

### Files to Modify

1. **`requirements.txt`**
   - Add `mac-vendor-lookup` dependency

2. **`app/models/dhcp_lease.py`**
   - Add `vendor: Optional[str]` attribute to `DhcpLease` class constructor
   - Update `to_dict()` method to include vendor information
   - Update `__init__` method signature

3. **`app/schemas/dhcp_lease_schema.py`**
   - Add `vendor` field to `DhcpLeaseSchema`
   - Include appropriate metadata and example

4. **`app/services/dhcp_service.py`**
   - Inject `MacVendorService` into `DhcpService` constructor
   - Update `_parse_lease_line()` method to lookup vendor information
   - Add vendor lookup to lease creation in `DhcpLease` instantiation

5. **`app/__init__.py`** (Flask app factory)
   - Register `MacVendorService` in application context
   - Initialize service during application startup

## Algorithm Details

### Simplified MAC Address Vendor Lookup

1. **Service Wrapper**:
   - `MacVendorService` acts as a simple wrapper around `mac-vendor-lookup` package
   - Handles exceptions and returns `None` for unknown vendors
   - No custom database management required

2. **Lookup Process**:
   - Call `MacLookup().lookup(mac_address)` from the package
   - Package handles OUI extraction, database lookup, and vendor matching internally
   - Returns vendor string directly or raises exception for unknown MACs

3. **Error Handling**:
   - Catch lookup exceptions and return `None` for graceful failure
   - Log warnings for lookup failures if needed
   - No impact on lease processing if vendor lookup fails

### Integration with Existing Lease Processing

1. **Service Integration**:
   - `DhcpService` receives `MacVendorService` instance via dependency injection
   - Vendor lookup performed during lease parsing in `_parse_lease_line()`
   - Vendor information stored as part of `DhcpLease` object

2. **Performance Considerations**:
   - Package handles database loading and caching internally
   - Minimal performance impact on lease processing
   - Graceful degradation if vendor lookup fails

## Implementation Phases

### Phase 1: Dependency and Service Setup
- Add `mac-vendor-lookup` to `requirements.txt`
- Create simple `MacVendorService` wrapper class
- Add vendor field to `DhcpLease` model and schema

### Phase 2: Integration with DHCP Service
- Integrate `MacVendorService` into `DhcpService`
- Update lease parsing to include vendor information
- Update API responses to include vendor data

## Implementation Example

### MacVendorService Implementation
```python
from mac_vendor_lookup import MacLookup
from typing import Optional
import logging

class MacVendorService:
    def __init__(self):
        self.lookup = MacLookup()
        self.logger = logging.getLogger(__name__)
    
    def get_vendor(self, mac_address: str) -> Optional[str]:
        try:
            return self.lookup.lookup(mac_address)
        except Exception as e:
            self.logger.debug(f"Vendor lookup failed for {mac_address}: {e}")
            return None
```

### Updated DhcpLease Object
```python
DhcpLease(
    ip_address="192.168.1.100",
    mac_address="aa:bb:cc:dd:ee:ff", 
    hostname="laptop-001",
    lease_time=datetime(...),
    client_id="01:aa:bb:cc:dd:ee:ff",
    is_static=False,
    pool_name="intranet",
    vendor="Apple, Inc."  # New field
)
```