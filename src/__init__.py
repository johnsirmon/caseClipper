"""
CaseClipSaver - Clipboard Monitor for Case Review Data

A lightweight Windows application that automatically monitors the clipboard
for case review data and saves it as structured .txt files.

Author: John Sirmon
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "John Sirmon"
__email__ = ""
__license__ = "MIT"

# Export main components
from .config import Config
from .data_parser import DataParser
from .file_manager import FileManager
from .clipboard_monitor import ClipboardMonitor
from .tray_ui import TrayUI

__all__ = [
    "Config",
    "DataParser", 
    "FileManager",
    "ClipboardMonitor",
    "TrayUI",
]
