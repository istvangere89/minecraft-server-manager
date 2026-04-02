"""Logging configuration for Minecraft Server Manager."""

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging():
    """Initialize file-based logging to msm_logs/ directory."""
    log_dir = Path("msm_logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "minecraft_server_manager.log"
    
    # Create logger
    logger = logging.getLogger("minecraft_server_manager")
    logger.setLevel(logging.DEBUG)
    
    # File handler with rotation (max 5MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler (WARNING level only, to not clutter terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger():
    """Get the configured logger instance."""
    return logging.getLogger("minecraft_server_manager")
