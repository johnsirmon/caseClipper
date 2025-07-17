"""
CaseClipSaver - Clipboard Monitor for Case Review Data
Main application entry point
"""
import sys
import os
import signal
import time
from pathlib import Path

# Handle imports for both development and PyInstaller executable
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    application_path = sys._MEIPASS
    sys.path.insert(0, application_path)
else:
    # Running in development
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try relative imports first (development)
    from .config import Config
    from .file_manager import FileManager
    from .clipboard_monitor import ClipboardMonitor
    from .tray_ui import TrayUI
except ImportError:
    # Fall back to absolute imports (PyInstaller)
    from config import Config
    from file_manager import FileManager
    from clipboard_monitor import ClipboardMonitor
    from tray_ui import TrayUI


class CaseClipSaver:
    """Main application class"""
    
    def __init__(self):
        """Initialize CaseClipSaver application"""
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
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start the tray UI (this will block until quit)
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
            # Stop tray UI (this will also stop clipboard monitoring)
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
    
    # Skip instance check if running as PyInstaller executable
    if not getattr(sys, 'frozen', False):
        # Check if another instance is already running (basic check) - only in development
        try:
            import psutil
            current_process = psutil.Process()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if (proc.info['pid'] != current_process.pid and 
                        proc.info['name'] and 'python' in proc.info['name'].lower() and
                        proc.info['cmdline'] and any('main.py' in str(cmd) for cmd in proc.info['cmdline'])):
                        print("Another instance of CaseClipSaver appears to be running.")
                        input("Press Enter to continue anyway, or Ctrl+C to exit...")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # psutil not available, skip check
            pass
    
    # Create and run application
    try:
        app = CaseClipSaver()
        app.run()
    except Exception as e:
        error_msg = f"Fatal error: {e}"
        print(error_msg)
        
        # Only show input prompt if not running as executable
        if not getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
