"""Application-specific configuration for DHCP monitoring.

This module implements app-specific configuration that is separate from the
infrastructure configuration in config.py.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class AppEnvironment(BaseSettings):
    """Raw environment variable loading for app-specific settings."""

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DNSMASQ_CONFIG_FILE_PATH: str = "/etc/dnsmasq.conf"
    ROOT_PATH: str = str(_PROJECT_ROOT)
    UPDATE_MAC_VENDOR_DATABASE: bool = True
    DEV_FAKE_LEASE_CHANGES: bool = False


class AppSettings(BaseModel):
    """Application-specific settings for DHCP monitoring."""

    model_config = ConfigDict(from_attributes=True)

    dnsmasq_config_file_path: str = "/etc/dnsmasq.conf"
    root_path: str = ""
    update_mac_vendor_database: bool = True
    dev_fake_lease_changes: bool = False

    @classmethod
    def load(cls, env: "AppEnvironment | None" = None, flask_env: str = "development") -> "AppSettings":
        """Load app settings from environment variables."""
        if env is None:
            env = AppEnvironment()

        update_mac_vendor = env.UPDATE_MAC_VENDOR_DATABASE
        dev_fake = env.DEV_FAKE_LEASE_CHANGES
        if flask_env == "development":
            if "UPDATE_MAC_VENDOR_DATABASE" not in env.model_fields_set:
                update_mac_vendor = False
            if "DEV_FAKE_LEASE_CHANGES" not in env.model_fields_set:
                dev_fake = True

        return cls(
            dnsmasq_config_file_path=env.DNSMASQ_CONFIG_FILE_PATH,
            root_path=env.ROOT_PATH,
            update_mac_vendor_database=update_mac_vendor,
            dev_fake_lease_changes=dev_fake,
        )
