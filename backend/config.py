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
    
    # Path configuration
    ROOT_PATH: str = os.environ.get('ROOT_PATH', '')
    
    # DHCP configuration paths
    DNSMASQ_CONFIG_FILE_PATH: str = os.environ.get('DNSMASQ_CONFIG_FILE_PATH', '/etc/dnsmasq.conf')
    
    # MAC vendor configuration
    UPDATE_MAC_VENDOR_DATABASE: bool = os.environ.get('UPDATE_MAC_VENDOR_DATABASE', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG: bool = True
    FLASK_ENV: str = 'development'
    DEV_FAKE_LEASE_CHANGES: bool = True


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG: bool = False
    FLASK_ENV: str = 'production'


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING: bool = True
    DEBUG: bool = True
    UPDATE_MAC_VENDOR_DATABASE: bool = False


def get_config() -> Type[Config]:
    """Get configuration class based on environment."""
    env: str = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)
