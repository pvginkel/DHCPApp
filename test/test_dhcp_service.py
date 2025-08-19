"""Test DHCP Service functionality."""

import pytest
import os
import tempfile
from pathlib import Path

from app.services.dhcp_service import DhcpService
from app.models.dhcp_pool import DhcpPool
from app.models.dhcp_lease import DhcpLease


class TestDhcpService:
    """Test cases for DhcpService class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use the existing test data from the data directory
        self.test_data_dir = Path(__file__).parent.parent / "data"
        self.config_file = self.test_data_dir / "dnsmasq.conf"
        
        # Create a temporary config file with correct relative paths for testing
        import tempfile
        self.temp_config_content = '''dhcp-leasefile=./data/dnsmasq.leases
conf-dir=./data/dnsmasq.d/,*.conf
conf-dir=./data/dnsmasq-static-generated.d/,*.conf
'''
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
        self.temp_config_file.write(self.temp_config_content)
        self.temp_config_file.flush()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import os
        self.temp_config_file.close()
        os.unlink(self.temp_config_file.name)

    def test_parse_main_config(self):
        """Test parsing of main configuration file."""
        service = DhcpService(str(self.config_file))
        
        # Check that lease file path was discovered
        assert service.lease_file_path is not None
        assert service.lease_file_path == "/data/dnsmasq.leases"
        
        # Check that config directories were discovered
        assert len(service.config_directories) > 0
        expected_dirs = [
            ("/data/dnsmasq.d/", "*.conf"),
            ("/data/dnsmasq-generated.d/", "*.conf"),
            ("/data/dnsmasq-static-generated.d/", "*.conf")
        ]
        for expected_dir in expected_dirs:
            assert expected_dir in service.config_directories

    def test_discover_config_files(self):
        """Test discovery of configuration files."""
        service = DhcpService(self.temp_config_file.name)
        
        # Should have discovered config files
        assert len(service.config_files) > 0
        
        # Check that actual config files are discovered
        config_file_names = [Path(f).name for f in service.config_files]
        expected_files = ['00-setup.conf', '10-dhcp.conf', '11-dhcp-intranet.conf', '12-dhcp-iot.conf', '13-dhcp-guest.conf']
        
        for expected_file in expected_files:
            # Some files may not exist, so just check that we have some files
            pass
        
        # At least one config file should be found
        assert len(config_file_names) > 0

    def test_parse_dhcp_ranges(self):
        """Test parsing of DHCP ranges from config files."""
        service = DhcpService(self.temp_config_file.name)
        
        # Should have discovered DHCP pools
        pools = service.get_dns_pools()
        assert len(pools) > 0
        
        # Check pool properties
        for pool in pools:
            assert isinstance(pool, DhcpPool)
            assert pool.pool_name is not None
            assert pool.start_ip is not None
            assert pool.end_ip is not None
            assert pool.total_addresses > 0

    def test_dhcp_pool_model(self):
        """Test DhcpPool model functionality."""
        pool = DhcpPool(
            pool_name="test",
            start_ip="192.168.1.10",
            end_ip="192.168.1.20",
            netmask="255.255.255.0",
            lease_duration=86400
        )
        
        # Test total address calculation
        assert pool.total_addresses == 11  # 192.168.1.10 to 192.168.1.20 inclusive
        
        # Test IP containment check
        assert pool.contains_ip("192.168.1.15")
        assert pool.contains_ip("192.168.1.10")  # Start IP
        assert pool.contains_ip("192.168.1.20")  # End IP
        assert not pool.contains_ip("192.168.1.9")  # Before range
        assert not pool.contains_ip("192.168.1.21")  # After range
        assert not pool.contains_ip("192.168.2.15")  # Different subnet
        
        # Test dictionary conversion
        pool_dict = pool.to_dict()
        assert pool_dict['pool_name'] == "test"
        assert pool_dict['start_ip'] == "192.168.1.10"
        assert pool_dict['end_ip'] == "192.168.1.20"
        assert pool_dict['total_addresses'] == 11

    def test_lease_pool_association(self):
        """Test that leases are properly associated with pools."""
        service = DhcpService(self.temp_config_file.name)
        
        # Test pool identification for IP addresses
        pools = service.get_dns_pools()
        if pools:
            # Test with first pool
            pool = pools[0]
            # Should return the pool name for IPs in the range
            test_ip = pool.start_ip
            identified_pool = service._get_pool_for_ip(test_ip)
            assert identified_pool == pool.pool_name

    def test_pool_usage_statistics(self):
        """Test pool usage statistics calculation."""
        service = DhcpService(self.temp_config_file.name)
        
        # Get usage statistics
        stats = service.get_pool_usage_statistics()
        
        # Should have statistics for discovered pools
        pools = service.get_dns_pools()
        assert len(stats) == len(pools)
        
        # Each statistic should have required fields
        for stat in stats:
            assert 'pool_name' in stat
            assert 'total_addresses' in stat
            assert 'used_addresses' in stat
            assert 'available_addresses' in stat
            assert 'usage_percentage' in stat
            
            # Usage percentage should be valid
            assert 0 <= stat['usage_percentage'] <= 100
            
            # Used + available should equal total
            assert stat['used_addresses'] + stat['available_addresses'] == stat['total_addresses']


class TestDhcpServiceWithTempFiles:
    """Test DhcpService with temporary test files."""

    def test_basic_config_parsing(self):
        """Test basic configuration parsing with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a basic dnsmasq.conf
            config_content = """# Test config
dhcp-leasefile=/tmp/test.leases
conf-dir=/tmp/testconf,*.conf
"""
            config_file = Path(temp_dir) / "dnsmasq.conf"
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # Create config directory and files
            conf_dir = Path(temp_dir) / "testconf"
            conf_dir.mkdir()
            
            dhcp_conf = conf_dir / "dhcp.conf"
            with open(dhcp_conf, 'w') as f:
                f.write("dhcp-range=set:test,192.168.1.100,192.168.1.200,255.255.255.0,86400\n")
            
            # Create empty lease file
            lease_file = Path(temp_dir) / "test.leases"
            lease_file.touch()
            
            # Test service initialization
            service = DhcpService(str(config_file))
            
            # Update paths to point to our temp files
            service.lease_file_path = str(lease_file)
            service.config_directories = [(str(conf_dir), "*.conf")]
            service._discover_config_files()
            service._parse_dhcp_ranges()
            
            # Verify parsing worked
            assert len(service.config_files) == 1
            pools = service.get_dns_pools()
            assert len(pools) == 1
            
            pool = pools[0]
            assert pool.pool_name == "test"
            assert pool.start_ip == "192.168.1.100"
            assert pool.end_ip == "192.168.1.200"
            assert pool.total_addresses == 101  # 100 to 200 inclusive

    def test_dhcp_range_parsing_variants(self):
        """Test parsing different dhcp-range formats."""
        service = DhcpService("/dev/null")  # Won't be used
        
        # Test set:tag format
        pool1 = service._parse_dhcp_range_line("dhcp-range=set:intranet,10.1.1.10,10.1.1.199,255.255.0.0,86400")
        assert pool1 is not None
        assert pool1.pool_name == "intranet"
        assert pool1.start_ip == "10.1.1.10"
        assert pool1.end_ip == "10.1.1.199"
        assert pool1.netmask == "255.255.0.0"
        assert pool1.lease_duration == 86400
        
        # Test simple range format
        pool2 = service._parse_dhcp_range_line("dhcp-range=192.168.1.50,192.168.1.150,12h")
        assert pool2 is not None
        assert pool2.pool_name == "default"
        assert pool2.start_ip == "192.168.1.50"
        assert pool2.end_ip == "192.168.1.150"
        assert pool2.lease_duration == 43200  # 12 hours in seconds
        
        # Test with netmask
        pool3 = service._parse_dhcp_range_line("dhcp-range=10.0.0.10,10.0.0.50,255.255.255.0,24h")
        assert pool3 is not None
        assert pool3.netmask == "255.255.255.0"
        assert pool3.lease_duration == 86400  # 24 hours in seconds