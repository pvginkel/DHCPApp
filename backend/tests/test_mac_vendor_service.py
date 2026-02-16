"""Tests for MacVendorService."""

from unittest.mock import Mock, patch


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
