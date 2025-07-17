"""
Configuration management for CaseClipSaver
"""
import json
import os
import sys
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for application settings"""
    
    DEFAULT_CONFIG = {
        "output_directory": "C:\\casedata\\",
        "polling_interval": 1.0,
        "file_encoding": "utf-8",
        "enable_notifications": True,
        "notification_sound": False,
        "auto_create_directory": True,
        "log_level": "INFO",
        "max_file_size_mb": 10,
        "context_processing_enabled": True,
        "context_processing_timeout": 30,
        "performance_mode": True
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration manager
        
        Args:
            config_path (str): Path to configuration file
        """
        if config_path is None:
            # Handle both development and PyInstaller executable
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable
                application_path = sys._MEIPASS
                config_path = os.path.join(application_path, "resources", "config.json")
            else:
                # Running in development
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    "resources", 
                    "config.json"
                )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = self.DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            else:
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value
        
        Args:
            key (str): Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    @property
    def output_directory(self) -> str:
        """Get output directory path"""
        return self.config["output_directory"]
    
    @property
    def polling_interval(self) -> float:
        """Get clipboard polling interval in seconds"""
        return self.config["polling_interval"]
    
    @property
    def file_encoding(self) -> str:
        """Get file encoding"""
        return self.config["file_encoding"]
    
    @property
    def enable_notifications(self) -> bool:
        """Get notification setting"""
        return self.config["enable_notifications"]
    
    @property
    def auto_create_directory(self) -> bool:
        """Get auto-create directory setting"""
        return self.config["auto_create_directory"]
    
    @property
    def notification_sound(self) -> bool:
        """Get notification sound setting"""
        return self.config["notification_sound"]
    
    @property
    def log_level(self) -> str:
        """Get log level"""
        return self.config["log_level"]
    
    @property
    def max_file_size_mb(self) -> int:
        """Get maximum file size in MB"""
        return self.config["max_file_size_mb"]
    
    @property
    def context_processing_enabled(self) -> bool:
        """Get context processing enabled setting"""
        return self.config["context_processing_enabled"]
    
    @property
    def context_processing_timeout(self) -> int:
        """Get context processing timeout in seconds"""
        return self.config["context_processing_timeout"]
    
    @property
    def performance_mode(self) -> bool:
        """Get performance mode setting"""
        return self.config["performance_mode"]
