"""MAC address vendor lookup service."""

import asyncio
import logging
import os
import tempfile
from urllib.parse import urlparse, urlunparse

from mac_vendor_lookup import OUI_URL, AsyncMacLookup, MacLookup


class MacVendorService:
    def __init__(self, update_database: bool = True, update_timeout: float = 15.0) -> None:
        # Set cross-platform cache path (workaround for library bug)
        cache_dir = tempfile.gettempdir()
        AsyncMacLookup.cache_path = os.path.join(cache_dir, "mac-vendors.txt")

        self.lookup = MacLookup()
        self.logger = logging.getLogger(__name__)
        self.lookups_enabled = True

        if update_database:
            self._update_database(update_timeout)

    def _update_database(self, timeout: float) -> None:
        """Update the OUI database from IEEE using secure HTTPS endpoint.

        Runs at startup, before the server binds, so the download is bounded:
        the library sets no timeout of its own. If the update leaves no vendor
        list on disk, lookups are switched off -- the library would otherwise
        retry the download on every lookup.
        """
        try:
            parsed = urlparse(OUI_URL)
            secure_url = urlunparse(parsed._replace(scheme="https"))
            self.logger.info(f"Updating MAC vendor database from: {secure_url}")

            self.lookup.loop.run_until_complete(
                asyncio.wait_for(self.lookup.async_lookup.update_vendors(url=secure_url), timeout)
            )
            self.logger.info("MAC vendor database updated successfully")

        except Exception as e:
            self.logger.warning(f"Failed to update MAC vendor database: {e!r}")

        if self.lookup.find_vendors_list() is None:
            self.logger.warning("No MAC vendor database available, vendor lookups disabled")
            self.lookups_enabled = False

    def get_vendor(self, mac_address: str) -> str | None:
        if not self.lookups_enabled:
            return None
        try:
            vendor: str = self.lookup.lookup(mac_address)
            return vendor
        except Exception as e:
            self.logger.debug(f"Vendor lookup failed for {mac_address}: {e}")
            return None
