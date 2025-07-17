"""
Logging system for CaseClipSaver
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .config import Config
except ImportError:
    from config import Config


class Logger:
    """Centralized logging system for the application"""
    
    _instance = None
    _logger = None
    
    def __new__(cls, config: Optional[Config] = None):
        """Singleton pattern for logger"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize logger
        
        Args:
            config (Config, optional): Application configuration
        """
        if self._initialized:
            return
        
        self.config = config
        self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self):
        """Set up the logging configuration"""
        # Create logs directory
        if self.config:
            log_dir = Path(self.config.output_directory).parent / "logs"
        else:
            log_dir = Path("logs")
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"caseclipsaver_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        log_level = getattr(logging, self.config.log_level.upper() if self.config else "INFO")
        
        # Create logger
        self._logger = logging.getLogger("CaseClipSaver")
        self._logger.setLevel(log_level)
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(file_handler)
        
        # Console handler (only in development)
        if not getattr(sys, 'frozen', False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(simple_formatter)
            self._logger.addHandler(console_handler)
        
        # Rotate old log files (keep last 7 days)
        self._rotate_logs(log_dir)
    
    def _rotate_logs(self, log_dir: Path):
        """Rotate old log files"""
        try:
            now = datetime.now()
            for log_file in log_dir.glob("caseclipsaver_*.log"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.split('_')[1]
                    log_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    # Delete files older than 7 days
                    if (now - log_date).days > 7:
                        log_file.unlink()
                        
                except (ValueError, IndexError):
                    # Skip files that don't match the expected format
                    continue
                    
        except Exception as e:
            # Don't let log rotation failures affect the application
            pass
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        if self._logger:
            self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        if self._logger:
            self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        if self._logger:
            self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        if self._logger:
            self._logger.exception(message, *args, **kwargs)
    
    @classmethod
    def get_logger(cls, config: Optional[Config] = None):
        """Get logger instance"""
        return cls(config)


# Global logger instance
logger = None


def get_logger(config: Optional[Config] = None):
    """Get the global logger instance"""
    global logger
    if logger is None:
        logger = Logger(config)
    return logger