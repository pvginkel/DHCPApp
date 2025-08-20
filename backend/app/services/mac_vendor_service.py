from mac_vendor_lookup import MacLookup, OUI_URL, AsyncMacLookup
from typing import Optional
import logging
import tempfile
import os
from urllib.parse import urlparse, urlunparse


class MacVendorService:
    def __init__(self, update_database: bool = True):
        # This doesn't make sense and is a bug in the library. This is the only way
        # to set the path where the database is stored.
        # Using cross-platform temporary directory instead of hardcoded /tmp/
        cache_dir = tempfile.gettempdir()
        AsyncMacLookup.cache_path = os.path.join(cache_dir, 'mac-vendors.txt')
        
        self.lookup = MacLookup()
        self.logger = logging.getLogger(__name__)

        if update_database:
            self._update_database()
    
    def _update_database(self) -> None:
        """Update the OUI database from IEEE using secure HTTPS endpoint."""
        try:
            # Convert HTTP URL to HTTPS for secure connection using proper URL parsing
            parsed = urlparse(OUI_URL)
            secure_url = urlunparse(parsed._replace(scheme='https'))
            self.logger.info(f"Updating MAC vendor database from: {secure_url}")
            
            self.lookup.update_vendors(url=secure_url)
            self.logger.info("MAC vendor database updated successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to update MAC vendor database: {e}")
            self.logger.info("Continuing with existing database")
    
    def get_vendor(self, mac_address: str) -> Optional[str]:
        try:
            return self.lookup.lookup(mac_address)
        except Exception as e:
            self.logger.debug(f"Vendor lookup failed for {mac_address}: {e}")
            return None