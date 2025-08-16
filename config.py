"""Configuration management class for the Flask application."""

import os
from typing import Type


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Application configuration
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '5000'))
    
    # DHCP configuration paths
    DHCP_LEASE_FILE_PATH: str = os.environ.get('DHCP_LEASE_FILE_PATH', '/var/lib/dhcp/dhcpd.leases')
    DHCP_CONFIG_FOLDER_PATH: str = os.environ.get('DHCP_CONFIG_FOLDER_PATH', '/etc/dnsmasq.d')


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG: bool = True
    FLASK_ENV: str = 'development'


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG: bool = False
    FLASK_ENV: str = 'production'


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING: bool = True
    DEBUG: bool = True


def get_config() -> Type[Config]:
    """Get configuration class based on environment."""
    env: str = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)
