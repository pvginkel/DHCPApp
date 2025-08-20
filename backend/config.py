"""Configuration management class for the Flask application."""

import os


class Config:
    """Base configuration class."""
    
    def __init__(self):
        # Flask configuration
        self.SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key')
        
        # Application configuration
        self.HOST: str = os.environ.get('HOST', '0.0.0.0')
        self.PORT: int = int(os.environ.get('PORT', '5000'))
        
        # Path configuration
        self.ROOT_PATH: str = os.environ.get('ROOT_PATH', '')
        
        # DHCP configuration paths
        self.DNSMASQ_CONFIG_FILE_PATH: str = os.environ.get('DNSMASQ_CONFIG_FILE_PATH', '/etc/dnsmasq.conf')
        
        # MAC vendor configuration
        self.UPDATE_MAC_VENDOR_DATABASE: bool = os.environ.get('UPDATE_MAC_VENDOR_DATABASE', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG: bool = True
        self.FLASK_ENV: str = 'development'
        self.DEV_FAKE_LEASE_CHANGES: bool = True
        self.UPDATE_MAC_VENDOR_DATABASE: bool = False  # Skip OUI database update in development for faster startup


class ProductionConfig(Config):
    """Production environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG: bool = False
        self.FLASK_ENV: str = 'production'


class TestingConfig(Config):
    """Testing environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.TESTING: bool = True
        self.DEBUG: bool = True
        self.UPDATE_MAC_VENDOR_DATABASE: bool = False


def get_config() -> Config:
    """Get configuration instance based on environment."""
    env: str = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()
