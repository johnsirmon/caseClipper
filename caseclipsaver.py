#!/usr/bin/env python3
"""
CaseClipSaver - Single-file clipboard monitoring application
A lightweight Windows application that monitors the clipboard for case review data
and automatically saves it as structured files.
"""

import os
import sys
import json
import re
import time
import threading
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Callable

# Third-party imports
import pyperclip
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem, Menu

# Optional notification support
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False


class Config:
    """Configuration management for CaseClipSaver"""
    
    DEFAULT_CONFIG = {
        "output_directory": "C:\\casedata\\",
        "polling_interval": 1.0,
        "file_encoding": "utf-8",
        "enable_notifications": True,
        "auto_create_directory": True,
        "max_file_size_mb": 10
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration"""
        if config_path is None:
            # Look for config.json in the same directory as the script
            config_path = Path(__file__).parent / "config.json"
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or return defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults
                merged_config = self.DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            else:
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    @property
    def output_directory(self) -> str:
        return self.config["output_directory"]
    
    @property
    def polling_interval(self) -> float:
        return self.config["polling_interval"]
    
    @property
    def file_encoding(self) -> str:
        return self.config["file_encoding"]
    
    @property
    def enable_notifications(self) -> bool:
        return self.config["enable_notifications"]
    
    @property
    def auto_create_directory(self) -> bool:
        return self.config["auto_create_directory"]
    
    @property
    def max_file_size_mb(self) -> int:
        return self.config["max_file_size_mb"]


class DataParser:
    """Parser for extracting ICM and Support Case IDs from text"""
    
    def __init__(self):
        """Initialize data parser with regex patterns"""
        self.patterns = {
            'icm_id': re.compile(r"ICM.*?(\d{9})", re.IGNORECASE),
            'case_id': re.compile(r"Support Request Number:\s*(\d{13,})", re.IGNORECASE),
            'alternative_case': re.compile(r"Case[:\s#]*(\d{13,})", re.IGNORECASE),
            'simple_case': re.compile(r"\b(\d{13,})\b"),
            'cri_pattern': re.compile(r"CRI[:\s]*(\d{13,})", re.IGNORECASE)
        }
    
    def extract_case_ids(self, text: str) -> Dict[str, Optional[str]]:
        """Extract ICM and Support Case IDs from text"""
        if not text or not isinstance(text, str):
            return {'icm_id': None, 'case_id': None}
        
        results = {}
        
        # Extract ICM ID
        icm_match = self.patterns['icm_id'].search(text)
        results['icm_id'] = icm_match.group(1) if icm_match else None
        
        # Extract Support Case ID (try multiple patterns)
        case_id = None
        for pattern_name in ['case_id', 'alternative_case', 'cri_pattern', 'simple_case']:
            match = self.patterns[pattern_name].search(text)
            if match:
                case_id = match.group(1)
                break
        
        results['case_id'] = case_id
        return results
    
    def is_valid_case_data(self, text: str) -> bool:
        """Check if text contains valid case review data"""
        if not text:
            return False
        
        ids = self.extract_case_ids(text)
        return ids['icm_id'] is not None or ids['case_id'] is not None
    
    def generate_filename(self, text: str) -> Optional[str]:
        """Generate filename from extracted IDs"""
        ids = self.extract_case_ids(text)
        
        if ids['icm_id'] and ids['case_id']:
            return f"{ids['icm_id']}_{ids['case_id']}.txt"
        elif ids['icm_id']:
            return f"ICM_{ids['icm_id']}.txt"
        elif ids['case_id']:
            return f"Case_{ids['case_id']}.txt"
        
        return None
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract metadata from case data"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text) if text else 0,
            'line_count': len(text.splitlines()) if text else 0
        }
        
        # Add extracted IDs
        ids = self.extract_case_ids(text)
        metadata.update(ids)
        
        return metadata


class FileManager:
    """Manages file operations for case data"""
    
    def __init__(self, config: Config):
        """Initialize file manager"""
        self.config = config
        self.output_dir = Path(config.output_directory)
        self.file_lock = threading.Lock()
        
        # Ensure output directory exists
        if config.auto_create_directory:
            self.ensure_output_directory()
    
    def ensure_output_directory(self) -> bool:
        """Ensure output directory exists"""
        try:
            with self.file_lock:
                self.output_dir.mkdir(parents=True, exist_ok=True)
                return True
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return False
    
    def save_case_data(self, content: str, filename: str) -> Tuple[bool, str]:
        """Save case data to file"""
        try:
            # Validate content size
            if len(content) > self.config.max_file_size_mb * 1024 * 1024:
                error_msg = f"Content too large: {len(content)} bytes"
                return False, error_msg
            
            if not self.ensure_output_directory():
                return False, "Could not create output directory"
            
            with self.file_lock:
                file_path = self.output_dir / filename
                
                # Handle duplicate files by appending timestamp
                if file_path.exists():
                    base_name = file_path.stem
                    extension = file_path.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{base_name}_{timestamp}{extension}"
                    file_path = self.output_dir / new_filename
                
                # Write content to file
                with open(file_path, 'w', encoding=self.config.file_encoding) as f:
                    f.write(content)
                
                return True, f"Saved to: {file_path}"
            
        except Exception as e:
            error_msg = f"Error saving file: {e}"
            return False, error_msg
    
    def save_with_metadata(self, content: str, filename: str, metadata: Dict) -> Tuple[bool, str]:
        """Save case data with metadata"""
        try:
            # Save main content file
            success, message = self.save_case_data(content, filename)
            if not success:
                return success, message
            
            # Save metadata file
            metadata_filename = filename.replace('.txt', '_metadata.json')
            metadata_path = self.output_dir / metadata_filename
            
            with open(metadata_path, 'w', encoding=self.config.file_encoding) as f:
                json.dump(metadata, f, indent=2)
            
            return True, f"Saved content and metadata"
            
        except Exception as e:
            error_msg = f"Error saving file with metadata: {e}"
            return False, error_msg
    
    def get_file_path(self, filename: str) -> Path:
        """Get full path for filename"""
        return self.output_dir / filename


class ClipboardMonitor:
    """Monitors clipboard for case review data"""
    
    def __init__(self, config: Config, file_manager: FileManager, 
                 on_data_processed: Optional[Callable] = None):
        """Initialize clipboard monitor"""
        self.config = config
        self.file_manager = file_manager
        self.data_parser = DataParser()
        self.on_data_processed = on_data_processed
        
        self.monitoring = False
        self.monitor_thread = None
        self.last_content = ""
        self.last_check_time = datetime.now()
        
        # Performance optimizations
        self.max_content_length = config.max_file_size_mb * 1024 * 1024
        self.content_hash_cache = set()
    
    def start_monitoring(self) -> bool:
        """Start clipboard monitoring"""
        if self.monitoring:
            return True
        
        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Clipboard monitoring started")
            return True
        except Exception as e:
            print(f"Error starting clipboard monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        print("Clipboard monitoring stopped")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.monitoring
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                current_content = self._get_clipboard_content()
                
                if current_content and current_content != self.last_content:
                    # Check content length limit
                    if len(current_content) > self.max_content_length:
                        print(f"Content too large ({len(current_content)} bytes), skipping")
                        continue
                    
                    # Check for duplicate content
                    content_hash = hash(current_content)
                    if content_hash not in self.content_hash_cache:
                        self.content_hash_cache.add(content_hash)
                        self._process_clipboard_content(current_content)
                        
                        # Limit cache size
                        if len(self.content_hash_cache) > 100:
                            self.content_hash_cache.clear()
                    
                    self.last_content = current_content
                
                self.last_check_time = datetime.now()
                time.sleep(self.config.polling_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.config.polling_interval)
    
    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content"""
        try:
            content = pyperclip.paste()
            return content if content else None
        except Exception as e:
            print(f"Error accessing clipboard: {e}")
            return None
    
    def _process_clipboard_content(self, content: str):
        """Process clipboard content for case data"""
        try:
            # Check if content contains valid case data
            if not self.data_parser.is_valid_case_data(content):
                return
            
            print("Valid case data detected!")
            
            # Extract IDs and generate filename
            filename = self.data_parser.generate_filename(content)
            if not filename:
                print("Could not generate filename")
                return
            
            print(f"Generated filename: {filename}")
            
            # Get metadata
            metadata = self.data_parser.extract_metadata(content)
            
            # Save the file
            success, message = self.file_manager.save_with_metadata(content, filename, metadata)
            
            # Prepare result data
            result_data = {
                'success': success,
                'message': message,
                'filename': filename,
                'content': content,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            # Call callback if provided
            if self.on_data_processed:
                self.on_data_processed(result_data)
            
            if success:
                print(f"✓ Case data saved: {filename}")
            else:
                print(f"✗ Failed to save case data: {message}")
                
        except Exception as e:
            error_msg = f"Error processing clipboard content: {e}"
            print(error_msg)
            
            if self.on_data_processed:
                self.on_data_processed({
                    'success': False,
                    'message': error_msg,
                    'filename': None,
                    'content': content,
                    'metadata': {},
                    'timestamp': datetime.now().isoformat()
                })
    
    def test_current_clipboard(self) -> Dict:
        """Test current clipboard content"""
        content = self._get_clipboard_content()
        
        if not content:
            return {
                'has_content': False,
                'is_valid_case_data': False,
                'message': 'No clipboard content'
            }
        
        is_valid = self.data_parser.is_valid_case_data(content)
        ids = self.data_parser.extract_case_ids(content)
        filename = self.data_parser.generate_filename(content) if is_valid else None
        
        return {
            'has_content': True,
            'content_length': len(content),
            'is_valid_case_data': is_valid,
            'extracted_ids': ids,
            'generated_filename': filename,
            'preview': content[:200] + '...' if len(content) > 200 else content,
            'message': 'Valid case data found' if is_valid else 'No valid case data found'
        }
    
    def get_status(self) -> Dict:
        """Get monitoring status"""
        return {
            'monitoring': self.monitoring,
            'last_check': self.last_check_time.isoformat(),
            'polling_interval': self.config.polling_interval,
            'output_directory': self.config.output_directory,
            'thread_alive': self.monitor_thread.is_alive() if self.monitor_thread else False
        }


class TrayUI:
    """System tray interface for CaseClipSaver"""
    
    def __init__(self, config: Config, clipboard_monitor: ClipboardMonitor, 
                 file_manager: FileManager):
        """Initialize tray UI"""
        self.config = config
        self.clipboard_monitor = clipboard_monitor
        self.file_manager = file_manager
        
        # Set up clipboard monitor callback
        self.clipboard_monitor.on_data_processed = self._on_data_processed
        
        self.icon = None
        self.running = False
        self._icon_cache = {}
    
    def _create_icon(self, active: bool = False) -> Image.Image:
        """Create tray icon image"""
        cache_key = f"icon_{active}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Create icon
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Choose color based on state
        color = (0, 255, 0, 255) if active else (128, 128, 128, 255)
        
        # Draw clipboard icon
        draw.rectangle([16, 20, 48, 56], fill=color, outline=(0, 0, 0, 255), width=2)
        draw.rectangle([24, 12, 40, 24], fill=color, outline=(0, 0, 0, 255), width=2)
        draw.rectangle([20, 28, 44, 52], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        
        # Add text
        if active:
            draw.text((18, 32), "ON", fill=(0, 0, 0, 255))
        else:
            draw.text((16, 32), "OFF", fill=(0, 0, 0, 255))
        
        self._icon_cache[cache_key] = image
        return image
    
    def _create_menu(self) -> Menu:
        """Create context menu"""
        monitoring = self.clipboard_monitor.is_monitoring()
        
        return Menu(
            MenuItem(
                "Turn OFF" if monitoring else "Turn ON",
                self._toggle_monitoring,
                default=True
            ),
            MenuItem("Test Clipboard", self._test_clipboard),
            Menu.SEPARATOR,
            MenuItem("Open Output Folder", self._open_output_folder),
            MenuItem("Status", self._show_status),
            Menu.SEPARATOR,
            MenuItem("Exit", self._quit_application)
        )
    
    def _toggle_monitoring(self, icon=None, item=None):
        """Toggle clipboard monitoring"""
        if self.clipboard_monitor.is_monitoring():
            self.clipboard_monitor.stop_monitoring()
            self._show_notification("CaseClipSaver", "Monitoring stopped")
        else:
            success = self.clipboard_monitor.start_monitoring()
            if success:
                self._show_notification("CaseClipSaver", "Monitoring started")
            else:
                self._show_notification("CaseClipSaver", "Failed to start monitoring")
        
        self._update_icon()
    
    def _test_clipboard(self, icon=None, item=None):
        """Test current clipboard content"""
        result = self.clipboard_monitor.test_current_clipboard()
        
        if result['has_content']:
            if result['is_valid_case_data']:
                message = f"Valid case data found!\nFilename: {result['generated_filename']}"
            else:
                message = "Clipboard contains text but no valid case data found"
        else:
            message = "No content in clipboard"
        
        self._show_notification("Clipboard Test", message)
    
    def _open_output_folder(self, icon=None, item=None):
        """Open output folder"""
        try:
            output_dir = self.config.output_directory
            if not os.path.exists(output_dir):
                self.file_manager.ensure_output_directory()
            
            os.startfile(output_dir)
        except Exception as e:
            self._show_notification("Error", f"Could not open folder: {e}")
    
    def _show_status(self, icon=None, item=None):
        """Show current status"""
        status = self.clipboard_monitor.get_status()
        monitoring = "ON" if status['monitoring'] else "OFF"
        
        message = (
            f"Monitoring: {monitoring}\n"
            f"Output: {self.config.output_directory}\n"
            f"Last check: {status['last_check'][:19]}"
        )
        
        self._show_notification("CaseClipSaver Status", message)
    
    def _quit_application(self, icon=None, item=None):
        """Quit the application"""
        self.stop()
    
    def _update_icon(self):
        """Update tray icon state"""
        if self.icon:
            monitoring = self.clipboard_monitor.is_monitoring()
            self.icon.icon = self._create_icon(monitoring)
            self.icon.menu = self._create_menu()
    
    def _on_data_processed(self, result_data: Dict):
        """Callback for processed data"""
        if not self.config.enable_notifications:
            return
        
        if result_data['success']:
            self._show_notification(
                "Case Data Saved",
                f"Saved: {result_data['filename']}"
            )
        else:
            self._show_notification(
                "Save Failed",
                result_data['message']
            )
    
    def _show_notification(self, title: str, message: str):
        """Show system notification"""
        print(f"{title}: {message}")
        
        if not self.config.enable_notifications or not NOTIFICATIONS_AVAILABLE:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=3,
                app_name="CaseClipSaver"
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def start(self):
        """Start the tray UI"""
        try:
            self.running = True
            
            # Start clipboard monitoring
            print("Starting clipboard monitoring...")
            monitor_success = self.clipboard_monitor.start_monitoring()
            if monitor_success:
                print("Clipboard monitoring started successfully")
            else:
                print("Warning: Failed to start clipboard monitoring")
            
            # Create tray icon
            initial_icon = self._create_icon(monitor_success)
            initial_menu = self._create_menu()
            
            self.icon = pystray.Icon(
                "CaseClipSaver",
                initial_icon,
                "CaseClipSaver - Clipboard Monitor",
                initial_menu
            )
            
            # Show startup notification
            if monitor_success:
                self._show_notification("CaseClipSaver", "Application started - Monitoring clipboard")
            else:
                self._show_notification("CaseClipSaver", "Application started - Click to start monitoring")
            
            # Run the icon (blocks until quit)
            self.icon.run()
            
        except Exception as e:
            print(f"Error starting tray UI: {e}")
            self.running = False
    
    def stop(self):
        """Stop the tray UI"""
        if not self.running:
            return
        
        self.running = False
        
        # Stop clipboard monitoring
        self.clipboard_monitor.stop_monitoring()
        
        # Stop tray icon
        if self.icon:
            self.icon.stop()
        
        print("Application stopped")


class CaseClipSaver:
    """Main application class"""
    
    def __init__(self):
        """Initialize CaseClipSaver"""
        print("Initializing CaseClipSaver...")
        
        # Load configuration
        self.config = Config()
        print(f"Output directory: {self.config.output_directory}")
        
        # Initialize components
        self.file_manager = FileManager(self.config)
        self.clipboard_monitor = ClipboardMonitor(self.config, self.file_manager)
        self.tray_ui = TrayUI(self.config, self.clipboard_monitor, self.file_manager)
        
        print("Components initialized successfully")
    
    def run(self):
        """Run the application"""
        try:
            print("Starting CaseClipSaver...")
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start the tray UI (blocks until quit)
            self.tray_ui.start()
            
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
            self.shutdown()
        except Exception as e:
            print(f"Error running application: {e}")
            self.shutdown()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Shutdown the application"""
        print("Shutting down CaseClipSaver...")
        
        try:
            self.tray_ui.stop()
            print("Application shutdown complete")
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        sys.exit(0)


def main():
    """Main entry point"""
    print("=" * 50)
    print("CaseClipSaver v1.0.0")
    print("Clipboard Monitor for Case Review Data")
    print("=" * 50)
    
    # Create and run application
    try:
        app = CaseClipSaver()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()