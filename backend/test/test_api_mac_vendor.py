"""Tests for MAC vendor lookup API integration."""

import pytest
from unittest.mock import Mock, patch
from app import create_app
from app.services.mac_vendor_service import MacVendorService


class TestApiMacVendorIntegration:
    """Test cases for API integration with MAC vendor lookup."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application."""
        # Create app with MAC vendor database update disabled for testing
        with patch.dict('os.environ', {
            'FLASK_ENV': 'testing',
            'DNSMASQ_CONFIG_FILE_PATH': 'data/dnsmasq.conf',
            'UPDATE_MAC_VENDOR_DATABASE': 'false'
        }):
            app = create_app()
            app.config['TESTING'] = True
            yield app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_leases_api_includes_vendor_field(self, app, client):
        """Test that /api/v1/leases includes vendor field in response."""
        with app.app_context():
            # Mock the MAC vendor service to return known values
            mock_vendor_service = Mock(spec=MacVendorService)
            mock_vendor_service.get_vendor.return_value = "Mock Vendor"
            
            # Replace the app's MAC vendor service with our mock
            app.mac_vendor_service = mock_vendor_service
            app.dhcp_service.mac_vendor_service = mock_vendor_service
            
            response = client.get('/api/v1/leases')
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Check response structure
            if isinstance(data, list):
                leases = data
            else:
                leases = data.get('leases', data.get('data', []))
            
            # If we have leases, verify vendor field is present
            if leases:
                for lease in leases:
                    assert 'vendor' in lease, "Vendor field missing from lease data"
                    # Vendor should be either the mocked value or None
                    assert lease['vendor'] in ["Mock Vendor", None]
    
    def test_leases_api_vendor_field_structure(self, app, client):
        """Test the structure and type of vendor field in API response."""
        with app.app_context():
            response = client.get('/api/v1/leases')
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Extract leases from response
            if isinstance(data, list):
                leases = data
            else:
                leases = data.get('leases', data.get('data', []))
            
            # Verify vendor field structure
            for lease in leases:
                assert 'vendor' in lease
                vendor = lease['vendor']
                # Vendor should be either a string or None
                assert vendor is None or isinstance(vendor, str)
    
    def test_leases_api_with_vendor_lookup_failure(self, app, client):
        """Test API response when vendor lookup fails."""
        with app.app_context():
            # Mock the MAC vendor service to always return None (lookup failure)
            mock_vendor_service = Mock(spec=MacVendorService)
            mock_vendor_service.get_vendor.return_value = None
            
            # Replace the app's MAC vendor service with our mock
            app.mac_vendor_service = mock_vendor_service
            app.dhcp_service.mac_vendor_service = mock_vendor_service
            
            response = client.get('/api/v1/leases')
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Extract leases from response
            if isinstance(data, list):
                leases = data
            else:
                leases = data.get('leases', data.get('data', []))
            
            # Verify that vendor field exists and is None for all leases
            for lease in leases:
                assert 'vendor' in lease
                assert lease['vendor'] is None
    
    def test_leases_api_without_mac_vendor_service(self, app, client):
        """Test API response when MAC vendor service is not available."""
        with app.app_context():
            # Remove MAC vendor service from DHCP service
            app.dhcp_service.mac_vendor_service = None
            
            response = client.get('/api/v1/leases')
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Extract leases from response
            if isinstance(data, list):
                leases = data
            else:
                leases = data.get('leases', data.get('data', []))
            
            # Verify that vendor field exists and is None for all leases
            for lease in leases:
                assert 'vendor' in lease
                assert lease['vendor'] is None
    
    def test_pool_usage_statistics_with_vendor_info(self, app, client):
        """Test that pool usage statistics API works with vendor lookup enabled."""
        with app.app_context():
            # Mock the MAC vendor service
            mock_vendor_service = Mock(spec=MacVendorService)
            mock_vendor_service.get_vendor.return_value = "Test Vendor"
            
            app.mac_vendor_service = mock_vendor_service
            app.dhcp_service.mac_vendor_service = mock_vendor_service
            
            response = client.get('/api/v1/pool-usage-statistics')
            assert response.status_code == 200
            
            # The endpoint should work regardless of vendor lookup
            data = response.get_json()
            assert isinstance(data, list)
    
    def test_openapi_spec_includes_vendor_field(self, app, client):
        """Test that OpenAPI specification includes vendor field."""
        response = client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        
        openapi_spec = response.get_json()
        
        # Navigate to DhcpLease schema definition
        schemas = openapi_spec.get('components', {}).get('schemas', {})
        lease_schema = schemas.get('DhcpLease', {})
        properties = lease_schema.get('properties', {})
        
        # Verify vendor field is in the schema
        assert 'vendor' in properties, "Vendor field missing from OpenAPI schema"
        
        vendor_field = properties['vendor']
        assert vendor_field.get('type') == 'string'
        assert 'nullable' in vendor_field or vendor_field.get('type') == ['string', 'null']
        assert 'description' in vendor_field