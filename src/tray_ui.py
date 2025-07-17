"""
System tray UI for CaseClipSaver
"""
import os
import sys
import threading
from typing import Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu

try:
    from .clipboard_monitor import ClipboardMonitor
    from .config import Config
    from .file_manager import FileManager
except ImportError:
    from clipboard_monitor import ClipboardMonitor
    from config import Config
    from file_manager import FileManager

# Try to import plyer for notifications, fall back gracefully
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Notifications not available - install plyer for notification support")


class TrayUI:
    """System tray interface for CaseClipSaver"""
    
    def __init__(self, config: Config, clipboard_monitor: ClipboardMonitor, 
                 file_manager: FileManager):
        """Initialize tray UI
        
        Args:
            config (Config): Application configuration
            clipboard_monitor (ClipboardMonitor): Clipboard monitor instance
            file_manager (FileManager): File manager instance
        """
        self.config = config
        self.clipboard_monitor = clipboard_monitor
        self.file_manager = file_manager
        
        # Set up clipboard monitor callback
        self.clipboard_monitor.on_data_processed = self._on_data_processed
        
        self.icon = None
        self.running = False
    
    def _create_icon(self, active: bool = False) -> Image.Image:
        """Create tray icon image
        
        Args:
            active (bool): Whether monitoring is active
            
        Returns:
            Image.Image: Icon image
        """
        # Create a simple icon with different colors for active/inactive states
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Choose color based on state
        color = (0, 255, 0, 255) if active else (128, 128, 128, 255)  # Green or Gray
        
        # Draw a simple clipboard icon
        # Clipboard base
        draw.rectangle([16, 20, 48, 56], fill=color, outline=(0, 0, 0, 255), width=2)
        # Clipboard clip
        draw.rectangle([24, 12, 40, 24], fill=color, outline=(0, 0, 0, 255), width=2)
        # Paper
        draw.rectangle([20, 28, 44, 52], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        
        # Add text indicator
        if active:
            draw.text((18, 32), "ON", fill=(0, 0, 0, 255))
        else:
            draw.text((16, 32), "OFF", fill=(0, 0, 0, 255))
        
        return image
    
    def _create_menu(self) -> Menu:
        """Create context menu for tray icon
        
        Returns:
            Menu: Tray icon context menu
        """
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
        """Toggle clipboard monitoring on/off"""
        if self.clipboard_monitor.is_monitoring():
            self.clipboard_monitor.stop_monitoring()
            self._show_notification("CaseClipSaver", "Monitoring stopped")
        else:
            success = self.clipboard_monitor.start_monitoring()
            if success:
                self._show_notification("CaseClipSaver", "Monitoring started")
            else:
                self._show_notification("CaseClipSaver", "Failed to start monitoring", error=True)
        
        # Update icon and menu
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
        """Open output folder in Windows Explorer"""
        try:
            output_dir = self.config.output_directory
            if not os.path.exists(output_dir):
                # Create directory if it doesn't exist
                self.file_manager.ensure_output_directory()
            
            os.startfile(output_dir)
        except Exception as e:
            self._show_notification("Error", f"Could not open folder: {e}", error=True)
    
    def _show_status(self, icon=None, item=None):
        """Show current status"""
        status = self.clipboard_monitor.get_status()
        monitoring = "ON" if status['monitoring'] else "OFF"
        
        message = (
            f"Monitoring: {monitoring}\n"
            f"Output: {self.config.output_directory}\n"
            f"Last check: {status['last_check'][:19]}"  # Trim microseconds
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
    
    def _on_data_processed(self, result_data: dict):
        """Callback for when clipboard data is processed
        
        Args:
            result_data (dict): Processing result data
        """
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
                result_data['message'],
                error=True
            )
    
    def _show_notification(self, title: str, message: str, error: bool = False):
        """Show system notification
        
        Args:
            title (str): Notification title
            message (str): Notification message
            error (bool): Whether this is an error notification
        """
        if not self.config.enable_notifications or not NOTIFICATIONS_AVAILABLE:
            print(f"{title}: {message}")
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5,
                app_name="CaseClipSaver"
            )
        except Exception as e:
            print(f"Notification error: {e}")
            print(f"{title}: {message}")
    
    def start(self):
        """Start the tray UI"""
        try:
            self.running = True
            
            # Start clipboard monitoring automatically
            print("Starting clipboard monitoring...")
            monitor_success = self.clipboard_monitor.start_monitoring()
            if monitor_success:
                print("Clipboard monitoring started successfully")
            else:
                print("Warning: Failed to start clipboard monitoring")
            
            # Create initial icon and menu
            initial_icon = self._create_icon(monitor_success)
            initial_menu = self._create_menu()
            
            # Create tray icon
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
            
            # Run the icon (this blocks until quit)
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
    
    def run_in_thread(self) -> threading.Thread:
        """Run tray UI in a separate thread
        
        Returns:
            threading.Thread: Thread running the tray UI
        """
        thread = threading.Thread(target=self.start, daemon=False)
        thread.start()
        return thread
