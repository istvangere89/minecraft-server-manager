"""
Server manager module for handling Bedrock server configurations and operations.
Manages config file discovery, parsing, copying, and server startup.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class ServerManager:
    """Manages Bedrock server configurations and operations."""
    
    CONFIG_PATTERN = re.compile(r"server-(.+)\.properties$")
    LEVEL_NAME_PATTERN = re.compile(r"level-name\s*=\s*(.+)")
    
    def __init__(self, server_directory: str):
        """
        Initialize server manager.
        
        Args:
            server_directory: Path to the Bedrock server directory
        """
        self.server_directory = Path(server_directory)
        self.server_properties = self.server_directory / "server.properties"
    
    def validate_server_directory(self) -> Tuple[bool, str]:
        """
        Validate that the server directory exists and contains bedrock_server.exe.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.server_directory.exists():
            return False, f"Server directory does not exist: {self.server_directory}"
        
        if not (self.server_directory / "bedrock_server.exe").exists():
            return False, "bedrock_server.exe not found in server directory"
        
        return True, ""
    
    def discover_configs(self) -> List[Dict[str, str]]:
        """
        Discover all available server-*.properties configurations.
        
        Returns:
            List of dicts with keys: 'config_file', 'world_name'
            Sorted by world_name
        """
        configs = []
        
        if not self.server_directory.exists():
            return configs
        
        # Find all server-*.properties files
        for file_path in self.server_directory.glob("server-*.properties"):
            config_name = file_path.name
            world_name = self._extract_world_name(file_path)
            
            if world_name:
                configs.append({
                    "config_file": config_name,
                    "world_name": world_name
                })
        
        # Sort by world name for consistent display
        configs.sort(key=lambda x: x["world_name"])
        return configs
    
    def _extract_world_name(self, config_path: Path) -> str:
        """
        Extract the world name from a server config file.
        Parses the 'level-name' property.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            World name if found, empty string otherwise
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    match = self.LEVEL_NAME_PATTERN.search(line)
                    if match:
                        return match.group(1).strip()
        except (IOError, UnicodeDecodeError):
            pass
        
        return ""
    
    def copy_config_to_active(self, config_file: str) -> Tuple[bool, str]:
        """
        Copy a server-*.properties file to server.properties.
        
        Args:
            config_file: Name of the config file (e.g., 'server-world1.properties')
            
        Returns:
            Tuple of (success, message)
        """
        source = self.server_directory / config_file
        
        if not source.exists():
            return False, f"Config file not found: {config_file}"
        
        try:
            shutil.copy2(source, self.server_properties)
            return True, f"Successfully loaded config: {config_file}"
        except (IOError, PermissionError) as e:
            return False, f"Failed to copy config: {str(e)}"
    
    def start_server(self) -> Tuple[bool, str]:
        """
        Start the Bedrock server in a new terminal window.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # On Windows, use 'start' command to open in new console window
            # Using shell=True is necessary for 'start' command
            subprocess.Popen(
                'start "Minecraft Bedrock Server" bedrock_server.exe',
                cwd=str(self.server_directory),
                shell=True
            )
            return True, "Server started in new window"
        except Exception as e:
            return False, f"Failed to start server: {str(e)}"
    
    def config_exists(self, config_file: str) -> bool:
        """
        Check if a config file exists.
        
        Args:
            config_file: Name of the config file
            
        Returns:
            True if config exists, False otherwise
        """
        return (self.server_directory / config_file).exists()
