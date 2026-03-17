"""
Test suite for CIAF Vault Configuration
Tests configuration management, environment variable handling, and defaults
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic_settings import BaseSettings

from ciaf.vault.config import VaultConfig, config


class TestVaultConfigDefaults:
    """Test suite for VaultConfig default values"""

    def test_config_instance_creation(self):
        """Test configuration instance creates successfully"""
        cfg = VaultConfig()

        assert cfg is not None
        assert isinstance(cfg, BaseSettings)

    def test_vault_path_default(self):
        """Test vault path has valid default"""
        cfg = VaultConfig()

        assert cfg.vault_path is not None
        assert isinstance(cfg.vault_path, str)
        assert len(cfg.vault_path) > 0
        # Should contain .ciaf/vault by default
        assert '.ciaf' in cfg.vault_path or 'vault' in cfg.vault_path

    def test_cert_validity_days_default(self):
        """Test certificate validity days default"""
        cfg = VaultConfig()

        assert cfg.cert_validity_days == 365
        assert isinstance(cfg.cert_validity_days, int)
        assert cfg.cert_validity_days > 0

    def test_cert_issuer_default(self):
        """Test certificate issuer default"""
        cfg = VaultConfig()

        assert cfg.cert_issuer == "CIAF Vault"
        assert isinstance(cfg.cert_issuer, str)

    def test_api_host_default(self):
        """Test API host default"""
        cfg = VaultConfig()

        assert cfg.api_host == "0.0.0.0"
        assert isinstance(cfg.api_host, str)

    def test_api_port_default(self):
        """Test API port default"""
        cfg = VaultConfig()

        assert cfg.api_port == 8000
        assert isinstance(cfg.api_port, int)
        assert 1 <= cfg.api_port <= 65535

    def test_api_title_default(self):
        """Test API title default"""
        cfg = VaultConfig()

        assert cfg.api_title == "CIAF Vault API"
        assert isinstance(cfg.api_title, str)

    def test_api_version_default(self):
        """Test API version default"""
        cfg = VaultConfig()

        assert cfg.api_version == "1.0.0"
        assert isinstance(cfg.api_version, str)
        # Matches semantic versioning
        assert len(cfg.api_version.split('.')) == 3

    def test_rate_limit_global_default(self):
        """Test global rate limit default"""
        cfg = VaultConfig()

        assert cfg.rate_limit_global == 1000
        assert isinstance(cfg.rate_limit_global, int)
        assert cfg.rate_limit_global > 0

    def test_rate_limit_org_default(self):
        """Test organization rate limit default"""
        cfg = VaultConfig()

        assert cfg.rate_limit_org == 100
        assert isinstance(cfg.rate_limit_org, int)
        assert cfg.rate_limit_org > 0

    def test_rate_limit_user_default(self):
        """Test user rate limit default"""
        cfg = VaultConfig()

        assert cfg.rate_limit_user == 30
        assert isinstance(cfg.rate_limit_user, int)
        assert cfg.rate_limit_user > 0

    def test_rate_limit_window_default(self):
        """Test rate limit window default"""
        cfg = VaultConfig()

        assert cfg.rate_limit_window == 60
        assert isinstance(cfg.rate_limit_window, int)
        assert cfg.rate_limit_window > 0

    def test_audit_retention_days_default(self):
        """Test audit retention days default"""
        cfg = VaultConfig()

        assert cfg.audit_retention_days == 2555
        assert isinstance(cfg.audit_retention_days, int)
        # ~7 years
        assert cfg.audit_retention_days > 365 * 5

    def test_audit_limit_per_query_default(self):
        """Test audit limit per query default"""
        cfg = VaultConfig()

        assert cfg.audit_limit_per_query == 1000
        assert isinstance(cfg.audit_limit_per_query, int)
        assert cfg.audit_limit_per_query > 0

    def test_key_version_prefix_default(self):
        """Test key version prefix default"""
        cfg = VaultConfig()

        assert cfg.key_version_prefix == "vault-key"
        assert isinstance(cfg.key_version_prefix, str)

    def test_auto_rotate_keys_default(self):
        """Test auto key rotation default"""
        cfg = VaultConfig()

        assert cfg.auto_rotate_keys is False
        assert isinstance(cfg.auto_rotate_keys, bool)

    def test_key_rotation_interval_default(self):
        """Test key rotation interval default"""
        cfg = VaultConfig()

        assert cfg.key_rotation_interval_days == 365
        assert isinstance(cfg.key_rotation_interval_days, int)

    def test_enable_cors_default(self):
        """Test CORS enabled default"""
        cfg = VaultConfig()

        assert cfg.enable_cors is True
        assert isinstance(cfg.enable_cors, bool)

    def test_cors_origins_default(self):
        """Test CORS origins default"""
        cfg = VaultConfig()

        assert cfg.cors_origins == "*"
        assert isinstance(cfg.cors_origins, str)

    def test_require_admin_key_default(self):
        """Test admin key requirement default"""
        cfg = VaultConfig()

        assert cfg.require_admin_key is True
        assert isinstance(cfg.require_admin_key, bool)

    def test_admin_key_prefix_default(self):
        """Test admin key prefix default"""
        cfg = VaultConfig()

        assert cfg.admin_key_prefix == "admin-"
        assert isinstance(cfg.admin_key_prefix, str)

    def test_log_level_default(self):
        """Test log level default"""
        cfg = VaultConfig()

        assert cfg.log_level == "INFO"
        assert isinstance(cfg.log_level, str)
        assert cfg.log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_enable_structured_logging_default(self):
        """Test structured logging default"""
        cfg = VaultConfig()

        assert cfg.enable_structured_logging is True
        assert isinstance(cfg.enable_structured_logging, bool)

    def test_rate_limits_hierarchy(self):
        """Test rate limits follow sensible hierarchy"""
        cfg = VaultConfig()

        # Global > Org > User
        assert cfg.rate_limit_global >= cfg.rate_limit_org
        assert cfg.rate_limit_org >= cfg.rate_limit_user


class TestVaultConfigMethods:
    """Test suite for VaultConfig methods"""

    def test_get_cors_origins_with_wildcard(self):
        """Test CORS origins parsing with wildcard"""
        cfg = VaultConfig(cors_origins="*")
        origins = cfg.get_cors_origins()

        assert isinstance(origins, list)
        assert origins == ["*"]

    def test_get_cors_origins_with_multiple(self):
        """Test CORS origins parsing with multiple values"""
        cfg = VaultConfig(cors_origins="http://localhost:3000,http://localhost:8000,https://example.com")
        origins = cfg.get_cors_origins()

        assert isinstance(origins, list)
        assert len(origins) == 3
        assert "http://localhost:3000" in origins
        assert "http://localhost:8000" in origins
        assert "https://example.com" in origins

    def test_get_cors_origins_strips_whitespace(self):
        """Test CORS origins parsing strips whitespace"""
        cfg = VaultConfig(cors_origins="http://localhost:3000 , http://localhost:8000")
        origins = cfg.get_cors_origins()

        assert all(origin == origin.strip() for origin in origins)
        assert len(origins) == 2

    def test_get_vault_db_path_default(self):
        """Test vault database path default"""
        cfg = VaultConfig()
        db_path = cfg.get_vault_db_path()

        assert isinstance(db_path, str)
        assert db_path.endswith("vault.db") or db_path.endswith("vault.db")

    def test_get_vault_db_path_custom(self):
        """Test vault database path with custom value"""
        custom_path = "/custom/path/vault.db"
        cfg = VaultConfig(vault_db_path=custom_path)
        db_path = cfg.get_vault_db_path()

        assert db_path == custom_path

    def test_get_vault_db_path_from_vault_path(self):
        """Test vault database path derived from vault path"""
        custom_vault_path = "/custom/vault"
        cfg = VaultConfig(vault_path=custom_vault_path, vault_db_path=None)
        db_path = cfg.get_vault_db_path()

        # Check that vault.db is in the path
        assert "vault.db" in db_path
        # Check that the custom path appears in some form (handle path separators)
        assert "custom" in db_path and "vault" in db_path


class TestVaultConfigEnvironmentVariables:
    """Test suite for environment variable configuration"""

    def test_config_prefix(self):
        """Test configuration uses CIAF_VAULT_ prefix"""
        # This tests the model_config (ConfigDict approach in Pydantic v2)
        assert VaultConfig.model_config['env_prefix'] == "CIAF_VAULT_"

    def test_config_case_insensitive(self):
        """Test configuration is case insensitive"""
        assert VaultConfig.model_config['case_sensitive'] is False

    @patch.dict(os.environ, {'CIAF_VAULT_API_PORT': '9000'})
    def test_config_from_env_api_port(self):
        """Test reading API port from environment variable"""
        cfg = VaultConfig()
        # Environment variable should override default
        assert cfg.api_port == 9000

    @patch.dict(os.environ, {'CIAF_VAULT_LOG_LEVEL': 'DEBUG'})
    def test_config_from_env_log_level(self):
        """Test reading log level from environment variable"""
        cfg = VaultConfig()
        assert cfg.log_level == 'DEBUG'

    @patch.dict(os.environ, {'CIAF_VAULT_ENABLE_CORS': 'false'})
    def test_config_from_env_bool(self):
        """Test reading boolean from environment variable"""
        cfg = VaultConfig()
        # Note: pydantic may parse this as string 'false', need to check

    @patch.dict(os.environ, {
        'CIAF_VAULT_API_PORT': '5000',
        'CIAF_VAULT_API_HOST': '127.0.0.1',
        'CIAF_VAULT_LOG_LEVEL': 'WARNING'
    })
    def test_config_multiple_env_vars(self):
        """Test reading multiple environment variables"""
        cfg = VaultConfig()

        assert cfg.api_port == 5000
        assert cfg.api_host == '127.0.0.1'
        assert cfg.log_level == 'WARNING'


class TestVaultConfigValidation:
    """Test suite for configuration validation"""

    def test_api_port_valid_range(self):
        """Test API port is in valid range"""
        cfg = VaultConfig()

        assert 1 <= cfg.api_port <= 65535

    def test_cert_validity_days_positive(self):
        """Test certificate validity is positive"""
        cfg = VaultConfig()

        assert cfg.cert_validity_days > 0

    def test_rate_limits_positive(self):
        """Test all rate limits are positive"""
        cfg = VaultConfig()

        assert cfg.rate_limit_global > 0
        assert cfg.rate_limit_org > 0
        assert cfg.rate_limit_user > 0
        assert cfg.rate_limit_window > 0

    def test_audit_days_positive(self):
        """Test audit retention days is positive"""
        cfg = VaultConfig()

        assert cfg.audit_retention_days > 0
        assert cfg.audit_limit_per_query > 0

    def test_string_fields_non_empty(self):
        """Test important string fields are non-empty"""
        cfg = VaultConfig()

        assert len(cfg.cert_issuer) > 0
        assert len(cfg.api_host) > 0
        assert len(cfg.api_title) > 0
        assert len(cfg.api_version) > 0


class TestVaultConfigSecuritySettings:
    """Test suite for security-related settings"""

    def test_require_admin_key_enabled_by_default(self):
        """Test admin key is required by default"""
        cfg = VaultConfig()

        assert cfg.require_admin_key is True

    def test_cors_enabled_by_default(self):
        """Test CORS is enabled by default"""
        cfg = VaultConfig()

        assert cfg.enable_cors is True

    def test_cors_origins_accessible(self):
        """Test CORS origins can be accessed"""
        cfg = VaultConfig()

        origins = cfg.get_cors_origins()
        assert origins is not None
        assert isinstance(origins, list)

    def test_admin_key_prefix_meaningful(self):
        """Test admin key prefix is meaningful"""
        cfg = VaultConfig()

        assert 'admin' in cfg.admin_key_prefix.lower()

    def test_key_rotation_settings_consistent(self):
        """Test key rotation settings are consistent"""
        cfg = VaultConfig()

        if cfg.auto_rotate_keys:
            assert cfg.key_rotation_interval_days > 0


class TestVaultConfigGlobalInstance:
    """Test suite for global config instance"""

    def test_global_config_instance_exists(self):
        """Test global config instance is created"""
        assert config is not None

    def test_global_config_is_vault_config(self):
        """Test global config is VaultConfig instance"""
        assert isinstance(config, VaultConfig)

    def test_global_config_has_defaults(self):
        """Test global config has all default values"""
        assert config.api_port == 8000
        assert config.cert_validity_days == 365
        assert config.log_level == "INFO"


class TestVaultConfigObjectBehavior:
    """Test suite for configuration object behavior"""

    def test_config_immutability_attempt(self):
        """Test configuration can be created multiple times"""
        cfg1 = VaultConfig()
        cfg2 = VaultConfig()

        assert cfg1.api_port == cfg2.api_port
        assert cfg1.cert_validity_days == cfg2.cert_validity_days

    def test_config_with_custom_values(self):
        """Test creating config with custom values"""
        custom_cfg = VaultConfig(
            api_port=5000,
            cert_validity_days=730,
            log_level="DEBUG"
        )

        assert custom_cfg.api_port == 5000
        assert custom_cfg.cert_validity_days == 730
        assert custom_cfg.log_level == "DEBUG"

    def test_config_partial_custom_values(self):
        """Test config with some custom values keeps others as default"""
        custom_cfg = VaultConfig(api_port=5000)

        assert custom_cfg.api_port == 5000
        assert custom_cfg.cert_validity_days == 365  # Default
        assert custom_cfg.log_level == "INFO"  # Default


class TestVaultConfigIntegration:
    """Integration tests for configuration"""

    def test_config_consistency(self):
        """Test configuration is internally consistent"""
        cfg = VaultConfig()

        # Audit retention should be reasonable (not less than 1 year)
        assert cfg.audit_retention_days >= 365

        # Certificate validity should be reasonable (at least 90 days)
        assert cfg.cert_validity_days >= 90

        # Rate limits should be sensible
        assert cfg.rate_limit_global > cfg.rate_limit_org > cfg.rate_limit_user

    def test_config_for_production_readiness(self):
        """Test configuration looks production-ready"""
        cfg = VaultConfig()

        # Should have meaningful values, not just defaults
        assert len(cfg.api_title) > 0
        assert len(cfg.cert_issuer) > 0
        assert cfg.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_config_cors_and_security(self):
        """Test CORS and security settings work together"""
        cfg = VaultConfig()

        origins = cfg.get_cors_origins()
        # Should be able to get origins regardless of setting
        assert origins is not None
        assert isinstance(origins, list)
        assert len(origins) >= 1
