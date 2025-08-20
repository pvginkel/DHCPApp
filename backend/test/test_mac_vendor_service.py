"""Tests for MAC vendor lookup service."""

import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import pytest

from app.services.mac_vendor_service import MacVendorService


class TestMacVendorService:
    """Test cases for MacVendorService."""
    
    def test_init_with_update_disabled(self):
        """Test initialization with database update disabled."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            
            assert service.lookup == mock_lookup
            assert service.logger is not None
            # Verify _update_database was not called
            mock_lookup.update_vendors.assert_not_called()
    
    def test_init_with_update_enabled(self):
        """Test initialization with database update enabled."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class, \
             patch.object(MacVendorService, '_update_database') as mock_update:
            mock_lookup = Mock()
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=True)
            
            assert service.lookup == mock_lookup
            mock_update.assert_called_once()
    
    def test_development_mode_skips_database_update(self):
        """Test that development mode skips database update by default."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup_class.return_value = mock_lookup
            
            # Test with update_database=False (as set in DevelopmentConfig)
            service = MacVendorService(update_database=False)
            
            assert service.lookup == mock_lookup
            # Verify _update_database was not called
            mock_lookup.update_vendors.assert_not_called()
    
    def test_cache_path_uses_temp_directory(self):
        """Test that cache path uses cross-platform temporary directory."""
        with patch('app.services.mac_vendor_service.MacLookup'), \
             patch('app.services.mac_vendor_service.AsyncMacLookup') as mock_async:
            
            MacVendorService(update_database=False)
            
            # Verify cache path was set to temp directory
            expected_path = os.path.join(tempfile.gettempdir(), 'mac-vendors.txt')
            assert mock_async.cache_path == expected_path
    
    def test_get_vendor_success(self):
        """Test successful vendor lookup."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup.lookup.return_value = "Apple, Inc."
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            result = service.get_vendor("00:1B:63:84:45:E6")
            
            assert result == "Apple, Inc."
            mock_lookup.lookup.assert_called_once_with("00:1B:63:84:45:E6")
    
    def test_get_vendor_failure(self):
        """Test vendor lookup failure handling."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup.lookup.side_effect = Exception("Vendor not found")
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            result = service.get_vendor("aa:bb:cc:dd:ee:ff")
            
            assert result is None
            mock_lookup.lookup.assert_called_once_with("aa:bb:cc:dd:ee:ff")
    
    def test_get_vendor_logs_debug_on_failure(self):
        """Test that vendor lookup failures are logged at debug level."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup.lookup.side_effect = Exception("Vendor not found")
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            
            with patch.object(service.logger, 'debug') as mock_debug:
                result = service.get_vendor("aa:bb:cc:dd:ee:ff")
                
                assert result is None
                mock_debug.assert_called_once()
                args = mock_debug.call_args[0][0]
                assert "aa:bb:cc:dd:ee:ff" in args
                assert "Vendor not found" in args
    
    @patch('app.services.mac_vendor_service.OUI_URL', 'http://example.com/oui.txt')
    def test_update_database_success(self):
        """Test successful database update with URL conversion."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            
            with patch.object(service.logger, 'info') as mock_info:
                service._update_database()
                
                # Verify URL was converted to HTTPS
                mock_lookup.update_vendors.assert_called_once_with(url='https://example.com/oui.txt')
                
                # Verify logging
                assert mock_info.call_count == 2
                assert "https://example.com/oui.txt" in mock_info.call_args_list[0][0][0]
                assert "successfully" in mock_info.call_args_list[1][0][0]
    
    @patch('app.services.mac_vendor_service.OUI_URL', 'https://example.com/oui.txt')
    def test_update_database_already_https(self):
        """Test database update with URL already using HTTPS."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            service._update_database()
            
            # Verify URL remains HTTPS
            mock_lookup.update_vendors.assert_called_once_with(url='https://example.com/oui.txt')
    
    def test_update_database_failure(self):
        """Test database update failure handling."""
        with patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
            mock_lookup = Mock()
            mock_lookup.update_vendors.side_effect = Exception("Network error")
            mock_lookup_class.return_value = mock_lookup
            
            service = MacVendorService(update_database=False)
            
            with patch.object(service.logger, 'warning') as mock_warning, \
                 patch.object(service.logger, 'info') as mock_info:
                
                service._update_database()
                
                # Verify error logging
                mock_warning.assert_called_once()
                assert "Network error" in mock_warning.call_args[0][0]
                
                # Verify info logging (should be called twice: URL and continuation message)
                assert mock_info.call_count == 2
                assert "Continuing with existing database" in mock_info.call_args[0][0]
    
    def test_url_parsing_edge_cases(self):
        """Test URL parsing with various edge cases."""
        test_cases = [
            ('http://example.com/path', 'https://example.com/path'),
            ('https://example.com/path', 'https://example.com/path'),
            ('ftp://example.com/path', 'https://example.com/path'),
            ('http://example.com:8080/path', 'https://example.com:8080/path'),
        ]
        
        for original_url, expected_url in test_cases:
            with patch('app.services.mac_vendor_service.OUI_URL', original_url), \
                 patch('app.services.mac_vendor_service.MacLookup') as mock_lookup_class:
                
                mock_lookup = Mock()
                mock_lookup_class.return_value = mock_lookup
                
                service = MacVendorService(update_database=False)
                service._update_database()
                
                mock_lookup.update_vendors.assert_called_with(url=expected_url)