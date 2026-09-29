"""Tests for MacVendorService."""

import asyncio
from collections.abc import Coroutine
from typing import Any
from unittest.mock import Mock, patch


def _unreachable(coro: Coroutine[Any, Any, Any]) -> None:
    """Stand in for the event loop when the OUI download cannot connect."""
    coro.close()
    raise OSError("unreachable")


class TestMacVendorService:
    """Test cases for MacVendorService."""

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_init_without_update(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        service = MacVendorService(update_database=False)
        mock_lookup_class.return_value.update_vendors.assert_not_called()
        assert service.lookup is not None

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_vendor_lookup_success(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        mock_instance = Mock()
        mock_instance.lookup.return_value = "Apple, Inc."
        mock_lookup_class.return_value = mock_instance

        service = MacVendorService(update_database=False)
        result = service.get_vendor("aa:bb:cc:dd:ee:ff")
        assert result == "Apple, Inc."

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_vendor_lookup_failure(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        mock_instance = Mock()
        mock_instance.lookup.side_effect = Exception("Not found")
        mock_lookup_class.return_value = mock_instance

        service = MacVendorService(update_database=False)
        result = service.get_vendor("00:00:00:00:00:00")
        assert result is None

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_failed_update_keeps_existing_database(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        mock_instance = Mock()
        mock_instance.loop.run_until_complete.side_effect = _unreachable
        mock_instance.find_vendors_list.return_value = "/tmp/mac-vendors.txt"
        mock_instance.lookup.return_value = "Apple, Inc."
        mock_lookup_class.return_value = mock_instance

        service = MacVendorService(update_database=True)
        assert service.get_vendor("aa:bb:cc:dd:ee:ff") == "Apple, Inc."

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_failed_update_without_database_disables_lookups(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        mock_instance = Mock()
        mock_instance.loop.run_until_complete.side_effect = _unreachable
        mock_instance.find_vendors_list.return_value = None
        mock_lookup_class.return_value = mock_instance

        service = MacVendorService(update_database=True)
        assert service.get_vendor("aa:bb:cc:dd:ee:ff") is None
        mock_instance.lookup.assert_not_called()

    @patch("app.services.mac_vendor_service.MacLookup")
    @patch("app.services.mac_vendor_service.AsyncMacLookup")
    def test_hanging_update_times_out(self, mock_async, mock_lookup_class) -> None:
        from app.services.mac_vendor_service import MacVendorService

        async def hang(url: str) -> None:
            await asyncio.sleep(60)

        loop = asyncio.new_event_loop()
        mock_instance = Mock()
        mock_instance.loop = loop
        mock_instance.async_lookup.update_vendors = hang
        mock_instance.find_vendors_list.return_value = None
        mock_lookup_class.return_value = mock_instance

        try:
            service = MacVendorService(update_database=True, update_timeout=0.05)
        finally:
            loop.close()

        assert service.get_vendor("aa:bb:cc:dd:ee:ff") is None
        mock_instance.lookup.assert_not_called()
