"""
Unit tests for Minecraft Server Manager modules.
Run with: python -m pytest tests/
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from config import ConfigManager
from password_manager import hash_password, verify_password
from server_manager import ServerManager


class TestPasswordManager:
    """Tests for password hashing and verification."""
    
    def test_hash_password_returns_string(self):
        """Verify hash_password returns a string."""
        result = hash_password("test_password")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 returns 64 hex chars
    
    def test_hash_password_consistent(self):
        """Verify same password produces same hash."""
        hash1 = hash_password("test")
        hash2 = hash_password("test")
        assert hash1 == hash2
    
    def test_hash_password_different_for_different_inputs(self):
        """Verify different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Verify correct password passes verification."""
        password = "my_secret_password"
        hash_val = hash_password(password)
        assert verify_password(password, hash_val) is True
    
    def test_verify_password_incorrect(self):
        """Verify incorrect password fails verification."""
        hash_val = hash_password("correct_password")
        assert verify_password("wrong_password", hash_val) is False
    
    def test_verify_password_case_sensitive(self):
        """Verify password verification is case sensitive."""
        hash_val = hash_password("Password")
        assert verify_password("password", hash_val) is False


class TestConfigManager:
    """Tests for configuration management."""
    
    def test_init_creates_default_config(self):
        """Verify default config is created if none exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "app_config.json"
            
            # Temporarily override CONFIG_FILE
            original_config_file = ConfigManager.CONFIG_FILE
            ConfigManager.CONFIG_FILE = str(config_file)
            
            try:
                config = ConfigManager()
                assert config.get_server_directory() == ""
                assert config.get_protected_configs() == {}
            finally:
                ConfigManager.CONFIG_FILE = original_config_file
    
    def test_set_and_get_server_directory(self):
        """Verify setting and getting server directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "app_config.json"
            ConfigManager.CONFIG_FILE = str(config_file)
            
            original_config_file = ConfigManager.CONFIG_FILE
            try:
                config = ConfigManager()
                test_path = "C:\\minecraft\\server"
                config.set_server_directory(test_path)
                
                # Reload config from file
                config2 = ConfigManager()
                assert config2.get_server_directory() == test_path
            finally:
                ConfigManager.CONFIG_FILE = original_config_file
    
    def test_set_and_get_password_for_config(self):
        """Verify setting and getting password hash for config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "app_config.json"
            ConfigManager.CONFIG_FILE = str(config_file)
            
            original_config_file = ConfigManager.CONFIG_FILE
            try:
                config = ConfigManager()
                config_name = "server-world1.properties"
                password_hash = hash_password("test_password")
                
                config.set_password_for_config(config_name, password_hash)
                
                # Verify it's protected
                assert config.is_config_protected(config_name) is True
                assert config.get_password_hash_for_config(config_name) == password_hash
            finally:
                ConfigManager.CONFIG_FILE = original_config_file
    
    def test_remove_password_for_config(self):
        """Verify removing password protection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "app_config.json"
            ConfigManager.CONFIG_FILE = str(config_file)
            
            original_config_file = ConfigManager.CONFIG_FILE
            try:
                config = ConfigManager()
                config_name = "server-world1.properties"
                password_hash = hash_password("test_password")
                
                config.set_password_for_config(config_name, password_hash)
                assert config.is_config_protected(config_name) is True
                
                config.remove_password_for_config(config_name)
                assert config.is_config_protected(config_name) is False
            finally:
                ConfigManager.CONFIG_FILE = original_config_file


class TestServerManager:
    """Tests for server management functionality."""
    
    def test_validate_server_directory_missing(self):
        """Verify validation fails for missing directory."""
        manager = ServerManager("/nonexistent/path")
        is_valid, error_msg = manager.validate_server_directory()
        assert is_valid is False
        assert "does not exist" in error_msg
    
    def test_validate_server_directory_no_executable(self):
        """Verify validation fails when bedrock_server.exe missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ServerManager(tmpdir)
            is_valid, error_msg = manager.validate_server_directory()
            assert is_valid is False
            assert "bedrock_server.exe" in error_msg
    
    def test_validate_server_directory_valid(self):
        """Verify validation passes with valid directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create bedrock_server.exe
            exe_path = Path(tmpdir) / "bedrock_server.exe"
            exe_path.touch()
            
            manager = ServerManager(tmpdir)
            is_valid, error_msg = manager.validate_server_directory()
            assert is_valid is True
            assert error_msg == ""
    
    def test_discover_configs_empty(self):
        """Verify empty list returned when no configs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ServerManager(tmpdir)
            configs = manager.discover_configs()
            assert configs == []
    
    def test_discover_configs_finds_properties(self):
        """Verify properties files are discovered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test config files
            config1 = Path(tmpdir) / "server-world1.properties"
            config1.write_text("level-name=World One\n")
            
            config2 = Path(tmpdir) / "server-world2.properties"
            config2.write_text("level-name=World Two\n")
            
            manager = ServerManager(tmpdir)
            configs = manager.discover_configs()
            
            assert len(configs) == 2
            assert configs[0]["world_name"] == "World One"
            assert configs[1]["world_name"] == "World Two"
    
    def test_discover_configs_sorted_by_world_name(self):
        """Verify configs are sorted alphabetically by world name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config1 = Path(tmpdir) / "server-zeta.properties"
            config1.write_text("level-name=Zeta\n")
            
            config2 = Path(tmpdir) / "server-alpha.properties"
            config2.write_text("level-name=Alpha\n")
            
            manager = ServerManager(tmpdir)
            configs = manager.discover_configs()
            
            assert configs[0]["world_name"] == "Alpha"
            assert configs[1]["world_name"] == "Zeta"
    
    def test_extract_world_name_valid(self):
        """Verify world name extraction from config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.properties"
            config_file.write_text("level-name=My World\n")
            
            manager = ServerManager(tmpdir)
            world_name = manager._extract_world_name(config_file)
            assert world_name == "My World"
    
    def test_extract_world_name_missing(self):
        """Verify empty string returned when level-name missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.properties"
            config_file.write_text("other-property=value\n")
            
            manager = ServerManager(tmpdir)
            world_name = manager._extract_world_name(config_file)
            assert world_name == ""
    
    def test_copy_config_to_active_success(self):
        """Verify config file copy operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "server-world.properties"
            source_file.write_text("level-name=Test World\n")
            
            manager = ServerManager(tmpdir)
            success, message = manager.copy_config_to_active("server-world.properties")
            
            assert success is True
            assert (Path(tmpdir) / "server.properties").exists()
    
    def test_copy_config_to_active_not_found(self):
        """Verify error handling for missing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ServerManager(tmpdir)
            success, message = manager.copy_config_to_active("nonexistent.properties")
            
            assert success is False
            assert "not found" in message.lower()
    
    def test_config_exists_true(self):
        """Verify config_exists returns True for existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "server-test.properties"
            config_file.touch()
            
            manager = ServerManager(tmpdir)
            assert manager.config_exists("server-test.properties") is True
    
    def test_config_exists_false(self):
        """Verify config_exists returns False for missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ServerManager(tmpdir)
            assert manager.config_exists("nonexistent.properties") is False


class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_password_config_workflow(self):
        """Test complete password protection workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "app_config.json"
            ConfigManager.CONFIG_FILE = str(config_file)
            
            original_config_file = ConfigManager.CONFIG_FILE
            try:
                config = ConfigManager()
                server_path = "C:\\minecraft"
                config.set_server_directory(server_path)
                
                # Set password
                password = "secret123"
                password_hash = hash_password(password)
                config_name = "server-survival.properties"
                config.set_password_for_config(config_name, password_hash)
                
                # Reload and verify
                config2 = ConfigManager()
                assert config2.get_server_directory() == server_path
                assert config2.is_config_protected(config_name)
                
                # Verify password
                stored_hash = config2.get_password_hash_for_config(config_name)
                assert verify_password(password, stored_hash)
                assert not verify_password("wrong_password", stored_hash)
            finally:
                ConfigManager.CONFIG_FILE = original_config_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
