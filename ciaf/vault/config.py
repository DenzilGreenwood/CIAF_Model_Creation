"""
Configuration management for CIAF Vault.

Supports environment-based configuration to avoid hardcoded values.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path


class VaultConfig(BaseSettings):
    """Vault configuration from environment variables."""

    model_config = ConfigDict(
        env_prefix="CIAF_VAULT_",
        case_sensitive=False,
        env_file=".env"
    )

    # Vault Storage
    vault_path: str = str(Path.home() / ".ciaf" / "vault")
    vault_db_path: Optional[str] = None

    # Certificate Configuration
    cert_validity_days: int = 365
    cert_issuer: str = "CIAF Vault"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "CIAF Vault API"
    api_version: str = "1.0.0"

    # Rate Limiting
    rate_limit_global: int = 1000  # requests/minute
    rate_limit_org: int = 100      # requests/minute per org
    rate_limit_user: int = 30      # requests/minute per user
    rate_limit_window: int = 60    # seconds

    # Audit Logging
    audit_retention_days: int = 2555  # ~7 years
    audit_limit_per_query: int = 1000

    # Key Management
    key_version_prefix: str = "vault-key"
    auto_rotate_keys: bool = False
    key_rotation_interval_days: int = 365

    # Security
    enable_cors: bool = True
    cors_origins: str = "*"  # Comma-separated list
    require_admin_key: bool = True
    admin_key_prefix: str = "admin-"

    # Logging
    log_level: str = "INFO"
    enable_structured_logging: bool = True

    def get_cors_origins(self) -> list:
        """Parse CORS origins from config."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_vault_db_path(self) -> str:
        """Get vault database path."""
        if self.vault_db_path:
            return self.vault_db_path
        return str(Path(self.vault_path) / "vault.db")


# Global configuration instance
config = VaultConfig()
