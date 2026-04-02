"""
Configuration management for the Minecraft Server Manager.
Handles loading and saving app configuration from/to minecraft_server_manager_config.json.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    """Manages application configuration and password hashes."""
    
    CONFIG_FILE = "minecraft_server_manager_config.json"
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_path = self._get_config_path()
        self.config = self._load_config()
    
    def _get_config_path(self) -> Path:
        """
        Get the config file path.
        Looks in app directory first (where exe is), then current directory.
        
        Returns:
            Path object for config file
        """
        # Try app directory first (where the exe is running from)
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller exe
            app_dir = Path(sys.executable).parent
            config_in_app_dir = app_dir / self.CONFIG_FILE
            if config_in_app_dir.exists():
                return config_in_app_dir
            # Use app directory as default location for new config
            return config_in_app_dir
        
        # Running as Python script - use current directory
        return Path(self.CONFIG_FILE)
    
    def _load_config(self) -> Dict:
        """
        Load configuration from JSON file.
        If file doesn't exist, return default config.
        
        Returns:
            Dictionary containing configuration
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh with defaults
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """
        Get default configuration structure.
        
        Returns:
            Dictionary with default config values
        """
        return {
            "server_directory": "",
            "protected_configs": {}
        }
    
    def save(self) -> None:
        """Save current configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_server_directory(self) -> str:
        """Get the server directory path."""
        return self.config.get("server_directory", "")
    
    def set_server_directory(self, path: str) -> None:
        """Set the server directory path."""
        self.config["server_directory"] = path
        self.save()
    
    def get_protected_configs(self) -> Dict[str, str]:
        """Get dict of protected config names and their password hashes."""
        return self.config.get("protected_configs", {})
    
    def set_password_for_config(self, config_name: str, password_hash: str) -> None:
        """
        Set or update password hash for a configuration.
        
        Args:
            config_name: Name of the configuration (e.g., 'server-world1.properties')
            password_hash: SHA256 hash of the password
        """
        if "protected_configs" not in self.config:
            self.config["protected_configs"] = {}
        self.config["protected_configs"][config_name] = password_hash
        self.save()
    
    def remove_password_for_config(self, config_name: str) -> None:
        """
        Remove password protection from a configuration.
        
        Args:
            config_name: Name of the configuration
        """
        if "protected_configs" in self.config:
            self.config["protected_configs"].pop(config_name, None)
            self.save()
    
    def is_config_protected(self, config_name: str) -> bool:
        """
        Check if a configuration is password protected.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            True if config has a password, False otherwise
        """
        return config_name in self.get_protected_configs()
    
    def get_password_hash_for_config(self, config_name: str) -> Optional[str]:
        """
        Get the password hash for a configuration.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Password hash if protected, None otherwise
        """
        return self.get_protected_configs().get(config_name)
